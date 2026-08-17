"""jobset_tab.py — Placeholder for Stage 3."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class JobsetTab(QWidget):
    def __init__(self, app_state=None, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "This workspace will be available in Stage 3."
        ))
