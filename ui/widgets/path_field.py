"""
path_field.py — A text field + Browse button for selecting a file or folder.

Token-aware mode
----------------
When constructed with a token provider, the field stores its value as a
{TOKEN}-relative path instead of a raw absolute path. On selection it rewrites
the chosen absolute path through core.token_resolver.tokenize_path():

  - anchor_token : the token this field is anchored to (e.g. KSG_COMPANY_DIR).
                   If the chosen path is under that token's directory, the
                   value becomes "{TOKEN}/relative/path". If it is NOT under
                   the anchor, the field emits anchor_violation(selected_path)
                   so the subtab can warn the user, and stores the best
                   available tokenization (or the raw path).
  - The Browse dialog is seeded from the resolved absolute path of the current
    value (or the anchor directory when empty), so the picker opens in the
    right place.

In plain mode (no token provider) it behaves exactly as before: stores and
shows the raw absolute path.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog


class PathField(QWidget):
    path_changed = Signal(str)
    #: emitted when a selection falls outside the anchor token's directory;
    #: payload is the selected absolute path
    anchor_violation = Signal(str)

    def __init__(self, mode: str = "folder", placeholder: str = "",
                 token_provider: Callable[[], dict] | None = None,
                 anchor_token: str | None = None,
                 parent=None) -> None:
        """
        mode           "folder" or "file"
        token_provider zero-arg callable returning the current token table
                       {TOKEN_NAME: absolute_dir}. When given, the field is
                       token-aware. Pass e.g. lambda: app_state.resolved_tokens.
        anchor_token   token this field is anchored to (e.g. "KSG_COMPANY_DIR").
        """
        super().__init__(parent)
        self._mode = mode
        self._token_provider = token_provider
        self._anchor_token = anchor_token

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.textChanged.connect(self.path_changed)
        label = "Choose Folder" if mode == "folder" else "Choose File"
        self._btn = QPushButton(label)
        self._btn.clicked.connect(self._browse)
        layout.addWidget(self._edit)
        layout.addWidget(self._btn)

    # ------------------------------------------------------------------
    # Value accessors (value is tokenized in token-aware mode)
    # ------------------------------------------------------------------

    def path(self) -> str:
        return self._edit.text().strip()

    def set_path(self, p: str) -> None:
        self._edit.setText(p)

    def _tokens(self) -> dict:
        if self._token_provider is None:
            return {}
        try:
            return self._token_provider() or {}
        except Exception:
            return {}

    def _resolve_for_seed(self) -> str:
        """Resolve the current (possibly tokenized) value to an absolute path
        suitable for seeding the file dialog."""
        from core.token_resolver import resolve_ref
        current = self.path()
        if current and self._token_provider is not None:
            resolved, _ = resolve_ref(current, self._tokens())
            current = resolved
        if current:
            cp = Path(current)
            if cp.is_dir():
                return str(cp)
            if cp.parent.is_dir():
                return str(cp.parent)
        # Empty value — seed from the anchor token's directory if available
        if self._anchor_token:
            base = self._tokens().get(self._anchor_token, "")
            if base and Path(base).is_dir():
                return base
        return ""

    # ------------------------------------------------------------------
    # Browse
    # ------------------------------------------------------------------

    def _browse(self) -> None:
        seed = self._resolve_for_seed()
        if self._mode == "folder":
            chosen = QFileDialog.getExistingDirectory(self, "Choose Folder", seed)
        else:
            chosen, _ = QFileDialog.getOpenFileName(self, "Choose File", seed)
        if not chosen:
            return

        if self._token_provider is None:
            # Plain mode — store the raw absolute path
            self.set_path(chosen)
            return

        # Token-aware mode — rewrite to a {TOKEN}-relative path
        from core.token_resolver import tokenize_path
        result, matched = tokenize_path(chosen, self._tokens(),
                                        prefer=self._anchor_token)
        self.set_path(result)
        if self._anchor_token and matched != self._anchor_token:
            # Selection is not under the anchor directory — let the subtab warn
            self.anchor_violation.emit(chosen)
