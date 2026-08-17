"""Headless integration test for setup.setup.run_setup."""
import pytest
from pathlib import Path
from unittest.mock import patch


def test_setup_headless_creates_local_config(tmp_path):
    """Verify setup creates kicad_specgen_local.json and company/users files."""
    kicad_config_dir = tmp_path / "kicad_config" / "9.0"
    kicad_config_dir.mkdir(parents=True)
    app_dir = tmp_path / "kicad_specgen"
    app_dir.mkdir()

    import setup.setup as setup_mod

    with patch.object(setup_mod, "resolve_kicad_common_dir",
                      return_value=(kicad_config_dir, "9.0")), \
         patch.object(setup_mod, "detect_platform", return_value="linux"), \
         patch("setup.setup_utils.create_venv", return_value=app_dir / ".venv"), \
         patch("setup.setup_utils.install_requirements"), \
         patch("setup.setup_linux.detect_kicad_cli", return_value=("", "")), \
         patch.object(setup_mod, "_PROJECT_ROOT", app_dir):
        result = setup_mod.run_setup(stage="stage1", launch=False)

    assert result == 0
    local_path = kicad_config_dir / "kicad_specgen_local.json"
    assert local_path.exists()

    # Verify writable tokens are left empty for the user to configure
    import core.specgen_local_config as lm
    cfg = lm.load(local_path)
    assert cfg.tokens["KSG_USER_SPECGEN_DIR"] == ""
    assert cfg.tokens["KSG_COMPANY_SPECGEN_DIR"] == ""
    assert cfg.tokens["KSG_APP_DIR"] == str(app_dir)
    assert cfg.setup_complete is True


def test_setup_with_seed_tokens(tmp_path):
    """Setup applies seeded writable tokens and active_user to local config."""
    from unittest.mock import patch
    import setup.setup as setup_mod

    kicad_config_dir = tmp_path / "kicad_config" / "9.0"
    kicad_config_dir.mkdir(parents=True)
    app_dir = tmp_path / "app"; app_dir.mkdir()
    company_dir = tmp_path / "CompanyRepo"; company_dir.mkdir()

    seed = {
        "KSG_COMPANY_DIR": str(company_dir),
        "KSG_COMPANY_SPECGEN_DIR": str(company_dir / "SpecGen" / "specgen"),
        "KSG_COMPANY_COMMON_DIR": str(company_dir / "SpecGen" / "common"),
        "KSG_USER_SPECGEN_DIR": str(company_dir / "SpecGen" / "Users" / "jsmith" / "specgen"),
        "KSG_USER_COMMON_DIR": str(company_dir / "SpecGen" / "Users" / "jsmith" / "common"),
        "active_user": "jsmith",
    }

    with patch.object(setup_mod, "resolve_kicad_common_dir",
                      return_value=(kicad_config_dir, "9.0")), \
         patch.object(setup_mod, "detect_platform", return_value="linux"), \
         patch("setup.setup_utils.create_venv", return_value=app_dir / ".venv"), \
         patch("setup.setup_utils.install_requirements"), \
         patch("setup.setup_linux.detect_kicad_cli", return_value=("", "")), \
         patch.object(setup_mod, "_PROJECT_ROOT", app_dir):
        rc = setup_mod.run_setup(stage="stage1", launch=False, seed_tokens=seed)

    assert rc == 0
    import core.specgen_local_config as lm
    cfg = lm.load(kicad_config_dir / "kicad_specgen_local.json")
    assert cfg.active_user == "jsmith"
    assert cfg.tokens["KSG_COMPANY_DIR"] == str(company_dir)
    assert cfg.tokens["KSG_USER_SPECGEN_DIR"] == seed["KSG_USER_SPECGEN_DIR"]
    assert cfg.tokens["KSG_COMPANY_SPECGEN_DIR"] == seed["KSG_COMPANY_SPECGEN_DIR"]
