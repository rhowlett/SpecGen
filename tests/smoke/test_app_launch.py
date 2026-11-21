# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_app_launch.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

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
