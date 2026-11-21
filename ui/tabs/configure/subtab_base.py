# v0.1
################################################################################
#  Project   : SpecGen
#  File      : subtab_base.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""
subtab_base.py — Base class and shared contract for Configure subtabs.

Every Configure subtab is a QWidget subclass that follows this contract so the
container (configuration_tab.py) can build, order, and refresh it without
knowing its internals.

CONTRACT
--------
Class attributes:
    TITLE : str      The tab label shown in the QTabWidget.
    ORDER : int      Sort key for left-to-right tab order (lower = earlier).

Constructor:
    __init__(self, app_state, config_service, validation_service)
        The container always passes all three services positionally. A subtab
        that does not need one simply ignores it.

Methods a subtab MAY override:
    populate(self)   Read from app_state and fill the widgets. Called by
                     refresh() ONLY when the subtab is not dirty, so unsaved
                     edits are never clobbered. Do all your app_state reads
                     here, not in __init__.

    on_save(self)    Persist the subtab's data through config_service. Called
                     when the subtab's Save button is clicked. After a
                     successful save, call self.mark_clean().

STICKINESS
----------
Subtab widgets are created once and kept alive for the lifetime of the
Configure tab. Switching between subtabs never destroys or recreates them, so
whatever the user typed remains in place. The only thing that could overwrite
unsaved edits is a populate() triggered by an external config reload — and the
base class suppresses that while the subtab is dirty (see refresh()).

DIRTY / GREEN SAVE BUTTON
-------------------------
Call self.mark_dirty() from any widget's change signal. This turns the
registered Save button green (theme.set_save_dirty) and stays green until
mark_clean() is called (normally from a successful on_save()).

Register the Save button once, in your subclass, with:
    self.register_save_button(self._btn_save)

HOW TO ADD A NEW SUBTAB
-----------------------
1. Create ui/tabs/configure/<name>_subtab.py.
2. Subclass SubtabBase, set TITLE and ORDER.
3. Build widgets in __init__ (call super().__init__ first).
4. Wire each editable widget's change signal to self.mark_dirty.
5. Register the Save button with self.register_save_button(...).
6. Implement populate() (read app_state) and on_save() (write config_service).
7. Register the class in configuration_tab.py's SUBTABS list.
That's the whole process — no other file needs to change.
"""
from __future__ import annotations

from PySide6.QtWidgets import QWidget, QPushButton


class SubtabBase(QWidget):
    TITLE: str = "Untitled"
    ORDER: int = 1000

    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(parent)
        self._state = app_state
        self._cs    = config_service
        self._vs    = validation_service
        self._dirty = False
        self._save_button: QPushButton | None = None

    # ------------------------------------------------------------------
    # Dirty-state management (shared by every subtab)
    # ------------------------------------------------------------------

    def register_save_button(self, button: QPushButton) -> None:
        """Register the Save button whose green state tracks dirtiness."""
        self._save_button = button
        self._apply_dirty_style()

    def mark_dirty(self, *args) -> None:
        """
        Mark the subtab as having unsaved changes. Accepts and ignores any
        arguments so it can be connected directly to Qt change signals
        (textChanged(str), currentIndexChanged(int), etc.).
        """
        if not self._dirty:
            self._dirty = True
            self._apply_dirty_style()

    def mark_clean(self) -> None:
        """Clear the unsaved-changes state (call after a successful save)."""
        if self._dirty:
            self._dirty = False
            self._apply_dirty_style()

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def _apply_dirty_style(self) -> None:
        if self._save_button is not None:
            from ui.theme import set_save_dirty
            set_save_dirty(self._save_button, self._dirty)

    # ------------------------------------------------------------------
    # Refresh entry point used by the container
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """
        Repopulate from app_state, but ONLY when the subtab is clean. This is
        what makes unsaved edits sticky: an external config reload will not
        wipe what the user is in the middle of editing.
        """
        if self._dirty:
            return
        self.populate()

    def force_populate(self) -> None:
        """Repopulate unconditionally and clear dirty (used by Discard)."""
        self.populate()
        self.mark_clean()

    # ------------------------------------------------------------------
    # Overridable hooks
    # ------------------------------------------------------------------

    def populate(self) -> None:
        """Read from app_state and fill widgets. Override in subclasses."""

    def on_save(self) -> None:
        """Persist via config_service. Override in subclasses."""
