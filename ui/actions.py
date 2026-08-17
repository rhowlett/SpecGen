"""
actions.py — QAction definitions and keyboard shortcuts.

macOS note: Qt moves any QAction with StandardKey.Quit to the system
application menu, hiding it from File. Fix: use QAction.MenuRole.NoRole
to keep Exit in the File menu on all platforms.
"""
from __future__ import annotations
import sys
from PySide6.QtGui import QAction, QKeySequence


class AppActions:
    def __init__(self, main_window, app_state, config_service,
                 validation_service) -> None:
        self._win   = main_window
        self._state = app_state
        self._cs    = config_service
        self._vs    = validation_service
        self._create_actions()
        self._connect_state()

    def _create_actions(self) -> None:
        w = self._win

        # --- File menu ---
        self.new_project   = QAction("New SpecGen Project...", w)
        self.open_project  = QAction("Open SpecGen Project...", w)
        self.open_project.setShortcut(QKeySequence.StandardKey.Open)
        self.save          = QAction("Save", w)
        self.save.setShortcut(QKeySequence.StandardKey.Save)
        self.save_as       = QAction("Save As...", w)
        self.close_project = QAction("Close Project", w)
        self.exit_app      = QAction("Exit", w)
        # NoRole prevents macOS from moving Exit to the application menu.
        # On macOS the conventional shortcut is Cmd+Q; on others Ctrl+Q.
        self.exit_app.setMenuRole(QAction.MenuRole.NoRole)
        self.exit_app.setShortcut(
            "Ctrl+Q" if sys.platform != "darwin" else "Meta+Q"
        )

        # --- Edit menu ---
        self.local_tokens    = QAction("Local Tokens...", w)
        self.resolve_missing = QAction("Resolve Missing Tokens...", w)
        self.kicad_cli       = QAction("Configure kicad-cli...", w)
        self.configure       = QAction("Configure", w)

        # --- View menu ---
        self.refresh = QAction("Refresh", w)
        self.refresh.setShortcut(QKeySequence("F5"))

        # --- Help menu ---
        self.help_index          = QAction("KiCad SpecGen Help", w)
        self.help_index.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_getting_started = QAction("Getting Started", w)
        self.help_tokens          = QAction("Project Setup and Tokens", w)
        self.help_configure       = QAction("Configure Tab", w)
        self.help_project         = QAction("Project Page", w)
        self.help_variables       = QAction("Variables and Jinja Templates", w)
        self.help_jobset          = QAction("Jobset", w)
        self.help_report          = QAction("Report and Fabrication", w)
        self.help_logs            = QAction("Logs", w)
        self.help_troubleshooting = QAction("Troubleshooting", w)
        self.open_logs_folder     = QAction("Open Logs Folder", w)
        self.about                = QAction("About KiCad SpecGen", w)

        # Stage 1: project operations disabled until a project is open
        for action in (self.save, self.save_as, self.close_project,
                       self.resolve_missing):
            action.setEnabled(False)

    def _connect_state(self) -> None:
        self._state.config_reloaded.connect(self._update_enabled_states)
        self._state.dirty_changed.connect(self._update_enabled_states)

    def _update_enabled_states(self) -> None:
        has_project = self._state.project_config is not None
        self.save.setEnabled(has_project and self._state.dirty_project)
        self.save_as.setEnabled(has_project)
        self.close_project.setEnabled(has_project)
        self.resolve_missing.setEnabled(bool(self._state.local_config))
