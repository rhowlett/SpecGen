# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_specgen_local_config.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Unit tests for core.specgen_local_config."""
import json, pytest
from pathlib import Path
from core.specgen_local_config import (
    load, save, create_minimal, validate_token_names,
    missing_required_tokens, LocalConfig,
)
FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_load_valid(tmp_path):
    src = FIXTURES / "sample_local.json"
    dst = tmp_path / "kicad_specgen_local.json"
    dst.write_bytes(src.read_bytes())
    cfg = load(dst)
    assert cfg.schema_version == 1
    assert cfg.active_user == "12345"
    assert "KSG_APP_DIR" in cfg.tokens


def test_load_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load(tmp_path / "no.json")


def test_save_roundtrip(tmp_path):
    src = FIXTURES / "sample_local.json"
    dst = tmp_path / "kicad_specgen_local.json"
    dst.write_bytes(src.read_bytes())
    cfg = load(dst)
    cfg.active_user = "99999"
    save(cfg)
    reloaded = load(dst)
    assert reloaded.active_user == "99999"


def test_create_minimal(tmp_path):
    p = tmp_path / "local.json"
    cfg = create_minimal(p, "/app", "/cfg", "/co", "linux")
    assert cfg.setup_complete is False
    assert p.exists()
    assert cfg.tokens["KSG_APP_DIR"] == "/app"
    assert cfg.tokens["KSG_COMPANY_DIR"] == "/co"
    # Writable-space tokens left empty for the user to configure
    assert cfg.tokens["KSG_USER_SPECGEN_DIR"] == ""
    assert cfg.tokens["KSG_COMPANY_SPECGEN_DIR"] == ""


def test_create_minimal_has_all_required_keys(tmp_path):
    from core.migrations import REQUIRED_LOCAL_TOKENS
    p = tmp_path / "local.json"
    cfg = create_minimal(p, "/app", "/cfg", "/co", "linux")
    for tok in REQUIRED_LOCAL_TOKENS:
        assert tok in cfg.tokens


def test_validate_token_names_ok():
    assert validate_token_names({"KSG_APP_DIR": "/some/path"}) == []


def test_validate_token_names_bad_pattern():
    errors = validate_token_names({"ksg_app_dir": "/path"})
    assert len(errors) == 1


def test_validate_token_names_protected():
    errors = validate_token_names({"KICAD_PROJECT_DIR": "/path"})
    assert any("protected" in e for e in errors)


def test_missing_required_tokens_all_present():
    tokens = {
        "KSG_APP_DIR": "/a", "KSG_SYSTEM_CONFIG_DIR": "/b",
        "KSG_COMPANY_DIR": "/c",
        "KSG_COMPANY_SPECGEN_DIR": "/cs", "KSG_COMPANY_COMMON_DIR": "/cc",
        "KSG_USER_SPECGEN_DIR": "/d", "KSG_USER_COMMON_DIR": "/e",
    }
    assert missing_required_tokens(tokens) == []


def test_missing_required_tokens_detects_missing():
    missing = missing_required_tokens({"KSG_APP_DIR": "/a"})
    assert "KSG_COMPANY_DIR" in missing
