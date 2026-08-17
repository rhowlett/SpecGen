"""
main_window.py — QMainWindow, sidebar, tab widget, menu bar, status bar.

Sidebar implemented as QListWidget with a non-selectable QFrame separator
between [Logs] and [Configure], per SpecGen_Application_Description.md.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path

from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QStatusBar,
    QMenuBar, QMenu, QFrame, QLabel,
)

from ui.actions import AppActions
from ui.tabs.configuration_tab import ConfigurationTab
from ui.tabs.logs_tab import LogsTab
from ui.tabs.project_tab import ProjectTab
from ui.tabs.variables_tab import VariablesTab
from ui.tabs.jobset_tab import JobsetTab
from ui.tabs.report_tab import ReportTab
from ui import theme as theme_mod

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, app_state, config_service, validation_service) -> None:
        super().__init__()
        self._state = app_state
        self._cs    = config_service
        self._vs    = validation_service

        self.setWindowTitle("KiCad SpecGen")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self._actions = AppActions(self, app_state, config_service, validation_service)
        self._build_central_widget()
        self._build_menu_bar()
        self._build_status_bar()
        self._connect_signals()
        log.info("MainWindow initialised")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self._sidebar = QListWidget()
        self._sidebar.setFixedWidth(150)
        self._sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sidebar_items = [
            ("Project",   "project"),
            ("Variables", "variables"),
            ("Jobset",    "jobset"),
            ("Report",    "report"),
            ("Logs",      "logs"),
            None,           # separator
            ("Configure", "configure"),
        ]
        for item in sidebar_items:
            if item is None:
                sep = QListWidgetItem()
                sep.setFlags(Qt.ItemFlag.NoItemFlags)
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                self._sidebar.addItem(sep)
                self._sidebar.setItemWidget(sep, line)
            else:
                label, key = item
                lw_item = QListWidgetItem(label)
                lw_item.setData(Qt.ItemDataRole.UserRole, key)
                lw_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._sidebar.addItem(lw_item)

        self._sidebar.currentItemChanged.connect(self._on_sidebar_changed)
        layout.addWidget(self._sidebar)

        # Stack
        self._stack = QStackedWidget()
        self._project_tab   = ProjectTab(self._state)
        self._variables_tab = VariablesTab(self._state)
        self._jobset_tab    = JobsetTab(self._state)
        self._report_tab    = ReportTab(self._state)
        self._logs_tab      = LogsTab()
        self._configure_tab = ConfigurationTab(
            self._state, self._cs, self._vs
        )
        for tab in (self._project_tab, self._variables_tab,
                    self._jobset_tab, self._report_tab,
                    self._logs_tab, self._configure_tab):
            self._stack.addWidget(tab)
        layout.addWidget(self._stack)

        # Select first real item (Project)
        self._sidebar.setCurrentRow(0)

    def _build_menu_bar(self) -> None:
        mb = self.menuBar()
        a  = self._actions
        ksg_app = ""
        if self._state.local_config:
            ksg_app = self._state.local_config.tokens.get("KSG_APP_DIR", "")

        # File
        file_menu = mb.addMenu("File")
        file_menu.addAction(a.new_project)
        file_menu.addAction(a.open_project)
        open_recent = file_menu.addMenu("Open Recent")
        open_recent.setEnabled(False)  # populated on config_reloaded
        file_menu.addSeparator()
        file_menu.addAction(a.save)
        file_menu.addAction(a.save_as)
        file_menu.addSeparator()
        file_menu.addAction(a.close_project)
        file_menu.addSeparator()
        file_menu.addAction(a.exit_app)

        # Edit
        edit_menu = mb.addMenu("Edit")
        edit_menu.addAction(a.local_tokens)
        edit_menu.addAction(a.resolve_missing)
        edit_menu.addSeparator()
        edit_menu.addAction(a.kicad_cli)
        edit_menu.addSeparator()
        edit_menu.addAction(a.configure)

        # View
        view_menu = mb.addMenu("View")
        view_menu.addAction(a.refresh)
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("Theme")
        for t in ("system","light","dark","engineering_dark","ion_dark","ion_light"):
            from PySide6.QtGui import QAction as _QA
            ta = _QA(t, self)
            ta.triggered.connect(lambda checked, name=t: self._set_theme(name))
            theme_menu.addAction(ta)
        view_menu.addSeparator()
        for label, key in [("Project","project"),("Variables","variables"),
                            ("Jobset","jobset"),("Report","report"),
                            ("Logs","logs"),("Configure","configure")]:
            from PySide6.QtGui import QAction as _QA2
            va = _QA2(label, self)
            va.triggered.connect(lambda checked, k=key: self._switch_to(k))
            view_menu.addAction(va)
        view_menu.addSeparator()
        diag_menu = view_menu.addMenu("Diagnostics")

        # Help
        help_menu = mb.addMenu("Help")
        help_menu.addAction(a.help_index)
        help_menu.addAction(a.help_getting_started)
        help_menu.addAction(a.help_tokens)
        help_menu.addAction(a.help_configure)
        help_menu.addSeparator()
        help_menu.addAction(a.help_project)
        help_menu.addAction(a.help_variables)
        help_menu.addAction(a.help_jobset)
        help_menu.addAction(a.help_report)
        help_menu.addAction(a.help_logs)
        help_menu.addAction(a.help_troubleshooting)
        help_menu.addSeparator()
        help_menu.addAction(a.open_logs_folder)
        help_menu.addSeparator()
        help_menu.addAction(a.about)

        # Connect actions
        a.exit_app.triggered.connect(self.close)
        a.local_tokens.triggered.connect(self._open_local_tokens)
        a.kicad_cli.triggered.connect(self._open_kicad_cli)
        a.configure.triggered.connect(lambda: self._switch_to("configure"))
        a.refresh.triggered.connect(self._refresh)
        a.new_project.triggered.connect(self._open_new_project)
        a.about.triggered.connect(self._open_about)
        a.open_logs_folder.triggered.connect(self._open_logs_folder)
        for action, path in [
            (a.help_index,           "help/index.md"),
            (a.help_getting_started, "help/getting_started.md"),
            (a.help_tokens,          "help/project_setup_tokens.md"),
            (a.help_configure,       "help/configure_tab.md"),
            (a.help_project,         "help/project_page.md"),
            (a.help_variables,       "help/variables_jinja.md"),
            (a.help_jobset,          "help/jobset.md"),
            (a.help_report,          "help/report.md"),
            (a.help_logs,            "help/logs.md"),
            (a.help_troubleshooting, "help/troubleshooting.md"),
        ]:
            action.triggered.connect(
                lambda checked, p=path, t=action.text(): self._open_help(p, t)
            )

    def _build_status_bar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_user  = QLabel("User: —")
        self._status_env   = QLabel("Env: —")
        sb.addWidget(self._status_user)
        sb.addWidget(QLabel(" | "))
        sb.addWidget(self._status_env)

    def _connect_signals(self) -> None:
        self._state.config_reloaded.connect(self._on_config_reloaded)
        self._state.dirty_changed.connect(self._update_title)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def _on_config_reloaded(self) -> None:
        self._update_title()
        user = self._state.active_user or "—"
        env  = self._state.active_environment or "—"
        cfg  = self._state.users_config
        if cfg:
            display = cfg.display_name(user)
            user = display or user
        self._status_user.setText(f"User: {user}")
        self._status_env.setText(f"Env: {env}")

    def _update_title(self) -> None:
        dirty = "• " if (self._state.dirty_project or self._state.dirty_local) else ""
        self.setWindowTitle(f"{dirty}KiCad SpecGen")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_sidebar_changed(self, current: QListWidgetItem,
                             previous: QListWidgetItem) -> None:
        if current is None:
            return
        if not (current.flags() & Qt.ItemFlag.ItemIsEnabled):
            # Separator — skip
            if previous:
                self._sidebar.blockSignals(True)
                self._sidebar.setCurrentItem(previous)
                self._sidebar.blockSignals(False)
            return
        key = current.data(Qt.ItemDataRole.UserRole)
        tab_map = {
            "project": self._project_tab,
            "variables": self._variables_tab,
            "jobset": self._jobset_tab,
            "report": self._report_tab,
            "logs": self._logs_tab,
            "configure": self._configure_tab,
        }
        tab = tab_map.get(key)
        if tab:
            self._stack.setCurrentWidget(tab)

    def _switch_to(self, key: str) -> None:
        for i in range(self._sidebar.count()):
            item = self._sidebar.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == key:
                self._sidebar.setCurrentItem(item)
                break

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _open_local_tokens(self) -> None:
        from ui.dialogs.local_tokens_dialog import LocalTokensDialog
        LocalTokensDialog(self._state, self._cs, self).exec()

    def _open_kicad_cli(self) -> None:
        from ui.dialogs.kicad_cli_dialog import KicadCliDialog
        KicadCliDialog(self._state, self._cs, self).exec()

    def _open_new_project(self) -> None:
        from ui.dialogs.new_project_dialog import NewProjectDialog
        NewProjectDialog(self).exec()

    def _open_about(self) -> None:
        from ui.dialogs.about_dialog import AboutDialog
        AboutDialog(self._state, self).exec()

    def _open_help(self, path: str, title: str) -> None:
        from ui.dialogs.help_dialog import HelpDialog
        ksg_app = ""
        if self._state.local_config:
            ksg_app = self._state.local_config.tokens.get("KSG_APP_DIR", "")
        HelpDialog(path, title, app_dir=ksg_app, parent=self).exec()

    def _open_logs_folder(self) -> None:
        import subprocess, sys
        ksg_app = ""
        if self._state.local_config:
            ksg_app = self._state.local_config.tokens.get("KSG_APP_DIR", "")
        folder = Path(ksg_app) / "logs" if ksg_app else Path("logs")
        folder.mkdir(parents=True, exist_ok=True)
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        elif sys.platform.startswith("win"):
            os.startfile(str(folder))
        else:
            subprocess.Popen(["xdg-open", str(folder)])

    def _set_theme(self, name: str) -> None:
        theme_mod.apply_theme(name)
        try:
            self._cs.save_preferences(name)
        except Exception:
            pass
        self._switch_to("configure")
        self._configure_tab.navigate_to_preferences()

    def _refresh(self) -> None:
        local = self._state.local_config
        if local and local.path:
            self._cs.load_all(local.path)
        log.info("Refresh completed")

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore[override]
        geo = self.geometry()
        geometry = {"x": geo.x(), "y": geo.y(),
                    "width": geo.width(), "height": geo.height()}
        project_ref = {}
        if self._state.local_config and self._state.local_config.last_session:
            project_ref = dict(self._state.local_config.last_session)
        try:
            self._cs.save_session(geometry, project_ref)
        except Exception as e:
            log.warning("Could not save last_session: %s", e)
        super().closeEvent(event)
