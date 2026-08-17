"""Integration tests for services.config_service."""
import pytest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from core.app_state import AppState
from services.config_service import ConfigService

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _make_local(tmp_path):
    src = FIXTURES / "sample_local.json"
    dst = tmp_path / "kicad_specgen_local.json"
    dst.write_bytes(src.read_bytes())
    return dst


def test_save_local_tokens(qapp, tmp_path):
    state = AppState()
    svc   = ConfigService(state)
    path  = _make_local(tmp_path)
    import core.specgen_local_config as local_mod
    state.local_config = local_mod.load(path)
    state.local_config.path = path
    new_tokens = {
        "KSG_APP_DIR":          "/new/app",
        "KSG_SYSTEM_CONFIG_DIR": "/new/cfg",
        "KSG_COMPANY_DIR":      "/new/co",
        "KSG_USER_SPECGEN_DIR": "/new/user",
        "KSG_USER_COMMON_DIR":  "/new/common",
    }
    with patch("core.specgen_local_config.save") as mock_save:
        import core.specgen_local_config as lm
        orig_load = lm.load
        def fake_load(p):
            c = lm.LocalConfig(**{k: v for k, v in state.local_config.__dict__.items()
                                   if not k.startswith('_') and k != 'path'})
            c.path = path
            c.tokens = new_tokens
            return c
        with patch.object(lm, "load", side_effect=fake_load):
            svc.save_local_tokens(new_tokens)
    assert state.local_config.tokens["KSG_APP_DIR"] == "/new/app"
    assert state.dirty_local is False


def test_save_preferences(qapp, tmp_path):
    state = AppState()
    svc   = ConfigService(state)
    path  = _make_local(tmp_path)
    import core.specgen_local_config as lm
    state.local_config = lm.load(path)
    state.local_config.path = path
    svc.save_preferences("light")
    reloaded = lm.load(path)
    assert reloaded.theme == "light"
