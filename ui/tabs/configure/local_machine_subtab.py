"""
local_machine_subtab.py — Local Machine subtab of the Configure tab.

Shows the KSG_* token table and kicad-cli information. All writes go through
config_service.save_local_tokens().
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QGroupBox, QMessageBox,
)

from ui.tabs.configure.subtab_base import SubtabBase
from ui.widgets.token_table import TokenTableWidget


class LocalMachineSubtab(SubtabBase):
    TITLE = "Local Machine"
    ORDER = 10

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(app_state, config_service, validation_service, parent)
        from ui.theme import make_section_heading
        layout = QVBoxLayout(self)

        layout.addWidget(make_section_heading("KiCad SpecGen Local Token Table"))
        layout.addWidget(QLabel(
            "KSG_* token definitions — absolute paths on this machine.\n"
            "★ = required   ✓ path exists   ⚠ path not found   ✗ empty"
        ))
        self._token_table = TokenTableWidget(edit_mode=True)
        self._token_table.tokens_changed.connect(self.mark_dirty)
        layout.addWidget(self._token_table)

        layout.addWidget(make_section_heading("kicad-cli Information"))
        cli_box = QGroupBox()
        clf = QFormLayout(cli_box)
        self._cli_path_label = QLabel()
        self._cli_path_label.setWordWrap(True)
        self._cli_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        self._cli_path_label.setMinimumWidth(400)
        self._cli_source_label  = QLabel()
        self._cli_version_label = QLabel()
        clf.addRow("Path:",    self._cli_path_label)
        clf.addRow("Source:",  self._cli_source_label)
        clf.addRow("Version:", self._cli_version_label)
        self._btn_configure_cli = QPushButton("Configure kicad-cli...")
        self._btn_configure_cli.clicked.connect(self._open_kicad_cli_dialog)
        clf.addRow(self._btn_configure_cli)
        layout.addWidget(cli_box)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save    = QPushButton("Save Local Changes")
        self._btn_discard = QPushButton("Discard Changes")
        self._btn_save.clicked.connect(self.on_save)
        self._btn_discard.clicked.connect(self.force_populate)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(self._btn_discard)
        layout.addLayout(btn_row)

        self.register_save_button(self._btn_save)

    def populate(self) -> None:
        cfg = self._state.local_config
        if not cfg:
            return
        self._token_table.set_tokens(cfg.tokens)
        self._cli_path_label.setText(cfg.tools.get("kicad_cli", "") or "(not configured)")
        self._cli_source_label.setText(cfg.tools.get("kicad_cli_source", "") or "—")
        self._cli_version_label.setText(cfg.tools.get("kicad_version", "") or "—")

    def on_save(self) -> None:
        tokens = self._token_table.get_tokens()
        try:
            self._cs.save_local_tokens(tokens)
            self.mark_clean()
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))

    def _open_kicad_cli_dialog(self) -> None:
        from ui.dialogs.kicad_cli_dialog import KicadCliDialog
        KicadCliDialog(self._state, self._cs, self).exec()
        # kicad-cli changes are saved by the dialog; re-read the cli labels
        self.populate()
