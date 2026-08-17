"""new_project_dialog.py — Stage 1 stub; full implementation in Stage 2."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox


class NewProjectDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New SpecGen Project")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "New project creation will be available in Stage 2.\n\n"
            "To open an existing project, use File → Open SpecGen Project..."
        ))
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)
