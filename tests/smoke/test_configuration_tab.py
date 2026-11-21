# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_configuration_tab.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Smoke test: Configuration tab opens, subtabs navigate, stickiness + green save."""
import pytest
from PySide6.QtWidgets import QApplication
from core.app_state import AppState
from services.config_service import ConfigService
from services.validation_service import ValidationService
from ui.tabs.configuration_tab import ConfigurationTab
from ui.tabs.configure.preferences_subtab import PreferencesSubtab
from ui.tabs.configure.company_subtab import CompanySubtab

pytestmark = pytest.mark.smoke


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_configuration_tab_shows(qapp, qtbot):
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    tab.show()
    assert tab.isVisible()


def test_configuration_tab_has_6_subtabs(qapp, qtbot):
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    assert tab._tabs.count() == 6


def test_subtab_order(qapp, qtbot):
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    titles = [tab._tabs.tabText(i) for i in range(tab._tabs.count())]
    assert titles == ["Local Machine", "Company", "Users",
                      "Environments", "Preferences", "Validation"]


def test_preferences_subtab_has_theme_combo(qapp, qtbot):
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    prefs = next(s for s in tab._subtabs if isinstance(s, PreferencesSubtab))
    assert prefs._theme_combo.count() == 6


def test_navigate_to_preferences(qapp, qtbot):
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    tab.navigate_to_preferences()
    assert isinstance(tab._subtabs[tab._tabs.currentIndex()], PreferencesSubtab)


def test_edit_marks_dirty_and_green(qapp, qtbot):
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    company = next(s for s in tab._subtabs if isinstance(s, CompanySubtab))
    assert company.is_dirty is False
    company._co_name_edit.setText("Changed")
    assert company.is_dirty is True
    assert company._btn_save.property("saveDirty") is True


def test_unsaved_edit_is_sticky_across_reload(qapp, qtbot):
    """A dirty subtab must not lose unsaved edits when config_reloaded fires."""
    state = AppState()
    tab = ConfigurationTab(state, ConfigService(state), ValidationService(state))
    qtbot.addWidget(tab)
    company = next(s for s in tab._subtabs if isinstance(s, CompanySubtab))
    company._co_name_edit.setText("Sticky Value")
    state.config_reloaded.emit()
    assert company._co_name_edit.text() == "Sticky Value"
