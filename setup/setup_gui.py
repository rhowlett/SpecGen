"""
setup_gui.py — GUI front-end for setup and uninstall.

Default mode for `python setup/setup.py`. Provides:
  - A setup window showing the six phases with progress and a summary.
  - An Uninstall dialog with two options (local-only or full) and confirmation.

The actual work is delegated to setup.setup.run_setup() and the uninstall
helpers in setup.setup_utils. This module only provides the GUI shell.
"""
from __future__ import annotations
import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QDialogButtonBox, QMessageBox,
    QGroupBox, QRadioButton, QWidget,
)

log = logging.getLogger("setup.gui")


class _QtLogToWidget(logging.Handler):
    """Routes setup log records into a QPlainTextEdit."""
    def __init__(self, widget: QPlainTextEdit):
        super().__init__()
        self._widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
            self._widget.appendPlainText(msg)
            QApplication.processEvents()
        except Exception:
            pass


class SetupWindow(QDialog):
    """Main setup window — runs setup and shows progress."""

    def __init__(self, stage: str = "stage1", parent=None) -> None:
        super().__init__(parent)
        self._stage = stage
        self.setWindowTitle("KiCad SpecGen — Setup")
        self.setMinimumSize(680, 480)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<h2>KiCad SpecGen Setup</h2>"))
        layout.addWidget(QLabel(
            "This will detect your platform, create a virtual environment, "
            "install dependencies, locate kicad-cli, and write the local "
            "configuration file."
        ))

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        layout.addWidget(self._log_view)

        btn_row = QHBoxLayout()
        self._btn_run       = QPushButton("Run Setup")
        self._btn_uninstall = QPushButton("Uninstall...")
        self._btn_launch    = QPushButton("Launch Application")
        self._btn_close     = QPushButton("Close")
        self._btn_launch.setEnabled(False)
        self._btn_run.clicked.connect(self._run_setup)
        self._btn_uninstall.clicked.connect(self._open_uninstall)
        self._btn_launch.clicked.connect(self._launch_app)
        self._btn_close.clicked.connect(self.accept)
        btn_row.addWidget(self._btn_run)
        btn_row.addWidget(self._btn_uninstall)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_launch)
        btn_row.addWidget(self._btn_close)
        layout.addLayout(btn_row)

    def _run_setup(self) -> None:
        from setup.setup import run_setup
        from core.platform_paths import detect_platform, resolve_kicad_common_dir
        self._btn_run.setEnabled(False)

        # Determine whether the local config already exists. If not, this is a
        # first run — open the company & user seeding dialog to gather the
        # writable-space tokens before running setup.
        seed_tokens = None
        try:
            platform = detect_platform()
            try:
                kc, _ = resolve_kicad_common_dir(platform)
            except ValueError:
                from core.platform_paths import kicad_common_dir
                kc = kicad_common_dir(platform, "9.0")
            local_path = kc / "kicad_specgen_local.json"

            if not local_path.exists():
                from setup.setup_seed_dialog import FirstRunSeedDialog
                app_dir = Path(__file__).resolve().parent.parent
                seed_dlg = FirstRunSeedDialog(app_dir, self)
                if seed_dlg.exec():
                    seed_tokens = seed_dlg.result_tokens
                else:
                    # User cancelled the first-run dialog — abort setup
                    self._log_view.appendPlainText(
                        "First-run setup cancelled — no changes made.")
                    self._btn_run.setEnabled(True)
                    return
        except Exception as e:
            log.warning("First-run seed check failed: %s", e)

        # Attach a temporary log handler to mirror setup output into the widget
        handler = _QtLogToWidget(self._log_view)
        handler.setLevel(logging.INFO)
        root = logging.getLogger()
        root.addHandler(handler)
        try:
            rc = run_setup(stage=self._stage, launch=False, seed_tokens=seed_tokens)
        finally:
            root.removeHandler(handler)

        if rc == 0:
            self._btn_launch.setEnabled(True)
            QMessageBox.information(self, "Setup Complete",
                                    "Setup completed successfully.")
        else:
            QMessageBox.warning(self, "Setup Failed",
                                "Setup encountered an error. See the log above.")
        self._btn_run.setEnabled(True)

    def _open_uninstall(self) -> None:
        UninstallDialog(self).exec()

    def _launch_app(self) -> None:
        import os, subprocess, sys
        app_dir = Path(__file__).resolve().parent.parent
        venv = Path(os.environ.get("SHARED_VENV") or app_dir / ".venv")
        venv_py = venv / "bin" / "python"
        if not venv_py.exists():
            venv_py = venv / "Scripts" / "python.exe"
        python = str(venv_py) if venv_py.exists() else sys.executable
        subprocess.Popen([python, str(app_dir / "app.py")], cwd=str(app_dir))
        self.accept()


class UninstallDialog(QDialog):
    """Uninstall dialog — local-only or full, with confirmation."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Uninstall KiCad SpecGen")
        self.setMinimumWidth(560)
        self._build_ui()

    def _build_ui(self) -> None:
        from core.platform_paths import detect_platform, resolve_kicad_common_dir
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h3>Uninstall KiCad SpecGen</h3>"))

        # Resolve paths to display
        self._app_dir = Path(__file__).resolve().parent.parent
        try:
            kc, _ = resolve_kicad_common_dir(detect_platform())
        except ValueError:
            from core.platform_paths import kicad_common_dir
            kc = kicad_common_dir(detect_platform(), "9.0")
        self._local_path = kc / "kicad_specgen_local.json"

        box = QGroupBox("Choose what to remove")
        bl = QVBoxLayout(box)
        self._radio_local = QRadioButton(
            "Remove local configuration only"
        )
        self._radio_local.setChecked(True)
        local_detail = QLabel(f"    Deletes: {self._local_path}")
        local_detail.setStyleSheet("color: gray;")

        self._radio_full = QRadioButton(
            "Full uninstall (remove application directory)"
        )
        full_detail = QLabel(
            f"    Deletes: {self._local_path}\n"
            f"    Deletes: {self._app_dir}  (entire application folder)"
        )
        full_detail.setStyleSheet("color: gray;")

        bl.addWidget(self._radio_local)
        bl.addWidget(local_detail)
        bl.addWidget(self._radio_full)
        bl.addWidget(full_detail)
        layout.addWidget(box)

        warn = QLabel(
            "⚠ This action cannot be undone. Your KiCad project files are "
            "not affected — only SpecGen application data is removed."
        )
        warn.setWordWrap(True)
        warn.setStyleSheet("color: #C0392B;")
        layout.addWidget(warn)

        buttons = QDialogButtonBox()
        self._btn_uninstall = buttons.addButton(
            "Uninstall", QDialogButtonBox.ButtonRole.DestructiveRole)
        self._btn_cancel = buttons.addButton(
            "Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        self._btn_uninstall.clicked.connect(self._do_uninstall)
        self._btn_cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _do_uninstall(self) -> None:
        from setup.setup_utils import uninstall_local_config, uninstall_full
        full = self._radio_full.isChecked()

        if full:
            prompt = (
                "Permanently delete the ENTIRE application directory?\n\n"
                f"{self._app_dir}\n\n"
                "This removes all SpecGen application files and the local "
                "configuration. This cannot be undone."
            )
        else:
            prompt = (
                "Remove the local configuration file?\n\n"
                f"{self._local_path}\n\n"
                "The application directory will be kept."
            )

        reply = QMessageBox.question(
            self, "Confirm Uninstall", prompt,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if full:
                summary = uninstall_full(self._app_dir, self._local_path)
                msg = (
                    f"Local config removed: {summary['local_removed']}\n"
                    f"Application directory removed: {summary['app_dir_removed']}"
                )
            else:
                removed = uninstall_local_config(self._local_path)
                msg = f"Local config removed: {removed}"
            QMessageBox.information(self, "Uninstall Complete", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Uninstall Failed", str(e))


def run_gui(stage: str = "stage1") -> int:
    """Launch the setup GUI. Returns process exit code."""
    app = QApplication.instance() or QApplication([])
    window = SetupWindow(stage=stage)
    window.show()
    return app.exec()
