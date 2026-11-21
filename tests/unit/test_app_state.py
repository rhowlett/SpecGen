# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_app_state.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Unit tests for core.app_state — signals fire correctly."""
import pytest
from PySide6.QtWidgets import QApplication
from core.app_state import AppState


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


def test_initial_state(qapp):
    state = AppState()
    assert state.local_config    is None
    assert state.company_config  is None
    assert state.resolved_tokens == {}
    assert state.dirty_project   is False
    assert state.dirty_local     is False
    assert state.setup_complete  is False


def test_config_reloaded_signal(qapp, qtbot):
    state = AppState()
    with qtbot.waitSignal(state.config_reloaded, timeout=1000):
        from core.specgen_local_config import LocalConfig
        cfg = LocalConfig()
        cfg.setup = {"setup_complete": False}
        state.set_local_config(cfg)


def test_dirty_changed_signal_project(qapp, qtbot):
    state = AppState()
    with qtbot.waitSignal(state.dirty_changed, timeout=1000):
        state.set_dirty_project(True)


def test_dirty_changed_signal_local(qapp, qtbot):
    state = AppState()
    with qtbot.waitSignal(state.dirty_changed, timeout=1000):
        state.set_dirty_local(True)


def test_dirty_not_emitted_if_unchanged(qapp):
    state = AppState()
    state.set_dirty_local(False)   # already False — should not emit
    count = [0]
    state.dirty_changed.connect(lambda: count.__setitem__(0, count[0] + 1))
    state.set_dirty_local(False)   # no change — no signal
    assert count[0] == 0


def test_tokens_changed_signal(qapp, qtbot):
    state = AppState()
    with qtbot.waitSignal(state.tokens_changed, timeout=1000):
        state.set_resolved_tokens({"KSG_APP_DIR": "/app"})


def test_setup_state_changed_signal(qapp, qtbot):
    state = AppState()
    from core.specgen_local_config import LocalConfig
    cfg = LocalConfig()
    cfg.setup = {"setup_complete": True}
    with qtbot.waitSignal(state.setup_state_changed, timeout=1000) as blocker:
        state.set_local_config(cfg)
    assert blocker.args[0] is True
