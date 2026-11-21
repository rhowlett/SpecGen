# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_validation_service.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Integration tests for services.validation_service."""
import pytest
from PySide6.QtWidgets import QApplication
from core.app_state import AppState
from core.specgen_local_config import LocalConfig
from services.validation_service import ValidationService


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_validation_with_no_config(qapp):
    state = AppState()
    svc   = ValidationService(state)
    report = svc.run_config_validation()
    assert report.failures > 0


def test_validation_complete_signal_fires(qapp, qtbot):
    state = AppState()
    svc   = ValidationService(state)
    with qtbot.waitSignal(state.validation_complete, timeout=2000) as blocker:
        svc.run_config_validation()
    assert blocker.args[0].overall in ("pass", "warn", "fail")
