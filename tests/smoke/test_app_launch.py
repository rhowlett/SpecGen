"""Smoke test: application starts and main window is visible."""
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from core.app_state import AppState
from services.config_service import ConfigService
from services.validation_service import ValidationService
from ui.main_window import MainWindow

pytestmark = pytest.mark.smoke


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_main_window_shows(qapp, qtbot):
    state  = AppState()
    cs     = ConfigService(state)
    vs     = ValidationService(state)
    window = MainWindow(state, cs, vs)
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()


def test_main_window_has_sidebar(qapp, qtbot):
    state  = AppState()
    cs     = ConfigService(state)
    vs     = ValidationService(state)
    window = MainWindow(state, cs, vs)
    qtbot.addWidget(window)
    sidebar = window.findChild(type(window._sidebar))
    assert sidebar is not None
