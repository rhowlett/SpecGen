"""local_tokens_dialog.py — Edit KSG_* tokens in kicad_specgen_local.json."""
from __future__ import annotations
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                                QDialogButtonBox, QMessageBox)
from core.specgen_local_config import validate_token_names, missing_required_tokens
from ui.widgets.token_table import TokenTableWidget


class LocalTokensDialog(QDialog):
    def __init__(self, app_state, config_service, parent=None) -> None:
        super().__init__(parent)
        self._state = app_state
        self._cs    = config_service
        self.setWindowTitle("Local Tokens")
        self.setMinimumWidth(680)
        self.resize(780, 500)
        self._build_ui()
        self._load_tokens()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "KSG_* token definitions (absolute paths).\n"
            "★ = required  |  Status: ✓ exists  ⚠ not found  ✗ invalid"
        ))
        self._table = TokenTableWidget(edit_mode=True)
        layout.addWidget(self._table)

        self._error_label = QLabel()
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        buttons = QDialogButtonBox()
        self._btn_save   = buttons.addButton("Save",   QDialogButtonBox.ButtonRole.AcceptRole)
        self._btn_cancel = buttons.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        self._btn_save.clicked.connect(self._save)
        self._btn_cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _load_tokens(self) -> None:
        cfg = self._state.local_config
        if cfg:
            self._table.set_tokens(cfg.tokens)

    def _save(self) -> None:
        tokens = self._table.get_tokens()
        errors = validate_token_names(tokens)
        missing = missing_required_tokens(tokens)
        if missing:
            errors.insert(0, f"Missing required tokens: {', '.join(missing)}")
        if errors:
            self._error_label.setText("\n".join(errors))
            self._error_label.setVisible(True)
            return
        try:
            self._cs.save_local_tokens(tokens)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", str(e))
