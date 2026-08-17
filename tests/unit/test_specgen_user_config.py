"""Unit tests for core.specgen_user_config."""
import pytest
from pathlib import Path
from core.specgen_user_config import (load, save, create_empty,
                                       derive_user_dirs, create_user_folders)

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_load_valid(tmp_path):
    dst = tmp_path / "users.json"
    dst.write_bytes((FIXTURES / "sample_users.json").read_bytes())
    cfg = load(dst)
    assert len(cfg.users) == 1
    assert cfg.users[0]["worker_id"] == "12345"
    assert cfg.users[0]["department"] == "hardware"
    assert cfg.users[0]["team"] == "power"


def test_get_user(tmp_path):
    dst = tmp_path / "users.json"
    dst.write_bytes((FIXTURES / "sample_users.json").read_bytes())
    cfg = load(dst)
    assert cfg.get_user("12345")["display_name"] == "John Smith"
    assert cfg.get_user("00000") is None


def test_create_empty(tmp_path):
    cfg = create_empty(tmp_path / "users.json")
    assert cfg.users == []


def test_derive_user_dirs():
    specgen, common = derive_user_dirs("/co", "12345")
    assert specgen.endswith("/SpecGen/Users/12345/specgen")
    assert common.endswith("/SpecGen/Users/12345/common")


def test_create_user_folders(tmp_path):
    specgen, common = create_user_folders(str(tmp_path), "12345")
    assert Path(specgen).is_dir()
    assert Path(common).is_dir()
