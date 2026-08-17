"""Smoke test: Logs tab shows and receives log entries."""
import logging
import pytest
from PySide6.QtWidgets import QApplication
from ui.tabs.logs_tab import LogsTab

pytestmark = pytest.mark.smoke


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_logs_tab_shows(qapp, qtbot):
    tab = LogsTab()
    qtbot.addWidget(tab)
    tab.show()
    assert tab.isVisible()


def test_logs_tab_receives_log_record(qapp, qtbot):
    from core.logging_utils import get_qt_handler
    tab = LogsTab()
    qtbot.addWidget(tab)
    handler = get_qt_handler()

    received = []
    handler.record_emitted.connect(
        lambda ts, lv, src, msg: received.append((lv, src, msg))
    )
    logging.getLogger("smoke_test").info("Smoke test log record")
    qapp.processEvents()
    assert any(msg == "Smoke test log record" for _, _, msg in received)
