"""
configuration_tab.py — Thin container for the Configure sidebar tab.

This file does NOT build any subtab content. Each subtab lives in its own file
under ui/tabs/configure/ and subclasses SubtabBase. This container only:
  1. instantiates the registered subtab classes (in ORDER),
  2. adds them to the QTabWidget, and
  3. refreshes them when app_state.config_reloaded fires.

────────────────────────────────────────────────────────────────────────────
HOW TO ADD A NEW SUBTAB
────────────────────────────────────────────────────────────────────────────
1. Create a new file:  ui/tabs/configure/<name>_subtab.py
2. In it, subclass SubtabBase (see ui/tabs/configure/subtab_base.py for the
   full contract). At minimum:

       from ui.tabs.configure.subtab_base import SubtabBase

       class MyThingSubtab(SubtabBase):
           TITLE = "My Thing"      # tab label
           ORDER = 25             # position among subtabs (lower = further left)

           def __init__(self, app_state, config_service, validation_service,
                        parent=None):
               super().__init__(app_state, config_service, validation_service, parent)
               # ... build widgets ...
               # wire each editable widget's change signal to self.mark_dirty
               # self.register_save_button(self._btn_save)

           def populate(self):
               # read from self._state (app_state) and fill widgets
               ...

           def on_save(self):
               # write through self._cs (config_service); then self.mark_clean()
               ...

3. Import the class below and add it to SUBTABS. That is the only edit needed
   in this file. ORDER controls position, so you do not need to insert it in
   any particular spot in the list.

────────────────────────────────────────────────────────────────────────────
STICKINESS & THE GREEN SAVE BUTTON (handled by SubtabBase — nothing to do here)
────────────────────────────────────────────────────────────────────────────
• Subtab widgets are created once and never destroyed while the Configure tab
  is alive, so switching subtabs preserves whatever the user typed, even if it
  was not saved.
• refresh() (called on config_reloaded) only repopulates a subtab when it is
  NOT dirty, so an external reload never clobbers unsaved edits.
• mark_dirty() turns the registered Save button green; mark_clean() (called
  after a successful on_save) clears it.
────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations
import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.tabs.configure.local_machine_subtab import LocalMachineSubtab
from ui.tabs.configure.company_subtab import CompanySubtab
from ui.tabs.configure.user_subtab import UserSubtab
from ui.tabs.configure.environments_subtab import EnvironmentsSubtab
from ui.tabs.configure.preferences_subtab import PreferencesSubtab
from ui.tabs.configure.validation_subtab import ValidationSubtab

log = logging.getLogger(__name__)

# Register subtab classes here. Order in this list does not matter — the
# container sorts by each class's ORDER attribute.
SUBTABS = [
    LocalMachineSubtab,
    CompanySubtab,
    UserSubtab,
    EnvironmentsSubtab,
    PreferencesSubtab,
    ValidationSubtab,
]


class ConfigurationTab(QWidget):
    def __init__(self, app_state, config_service, validation_service,
                 parent=None) -> None:
        super().__init__(parent)
        self._state = app_state
        self._cs    = config_service
        self._vs    = validation_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Instantiate subtabs in ORDER and add them to the tab widget.
        self._subtabs: list = []
        for cls in sorted(SUBTABS, key=lambda c: c.ORDER):
            subtab = cls(app_state, config_service, validation_service)
            self._tabs.addTab(subtab, subtab.TITLE)
            self._subtabs.append(subtab)

        app_state.config_reloaded.connect(self._refresh_all)
        # Populate immediately — config_reloaded may have already fired during
        # app.py startup before this tab existed.
        self._refresh_all()

    def _refresh_all(self) -> None:
        for subtab in self._subtabs:
            subtab.refresh()

    def navigate_to_preferences(self) -> None:
        """Called by View → Theme to focus the Preferences subtab."""
        for i, subtab in enumerate(self._subtabs):
            if isinstance(subtab, PreferencesSubtab):
                self._tabs.setCurrentIndex(i)
                return
