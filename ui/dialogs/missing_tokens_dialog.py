"""missing_tokens_dialog.py — Stage 1 stub; full implementation in Stage 2."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class MissingTokensDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Missing Tokens")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Token resolution requires an open project.\n"
            "Open a project to use this feature."
        ))
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)
