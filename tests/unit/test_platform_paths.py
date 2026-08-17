"""Unit tests for core.platform_paths."""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.platform_paths import (
    detect_platform, kicad_config_parent, detect_kicad_config_version,
    kicad_common_dir, resolve_kicad_common_dir,
    PLATFORM_MACOS, PLATFORM_LINUX, PLATFORM_WINDOWS,
)


def test_detect_platform_macos():
    with patch.object(sys, "platform", "darwin"):
        assert detect_platform() == PLATFORM_MACOS


def test_detect_platform_linux():
    with patch.object(sys, "platform", "linux"):
        assert detect_platform() == PLATFORM_LINUX


def test_detect_platform_windows():
    with patch.object(sys, "platform", "win32"):
        assert detect_platform() == PLATFORM_WINDOWS


def test_kicad_common_dir_macos():
    path = kicad_common_dir(PLATFORM_MACOS, "9.0")
    assert path.parts[-1] == "9.0"
    assert "kicad" in str(path).lower()


def test_kicad_common_dir_linux():
    path = kicad_common_dir(PLATFORM_LINUX, "9.0")
    assert "9.0" in str(path)


def test_detect_version_selects_highest(tmp_path):
    (tmp_path / "8.0").mkdir()
    (tmp_path / "9.0").mkdir()
    (tmp_path / "9.1").mkdir()
    (tmp_path / "not_a_version").mkdir()
    with patch("core.platform_paths.kicad_config_parent", return_value=tmp_path):
        version = detect_kicad_config_version(PLATFORM_LINUX)
    assert version == "9.1"


def test_detect_version_returns_none_when_no_dirs(tmp_path):
    with patch("core.platform_paths.kicad_config_parent", return_value=tmp_path):
        version = detect_kicad_config_version(PLATFORM_LINUX)
    assert version is None


def test_resolve_raises_when_no_config_dir(tmp_path):
    empty = tmp_path / "kicad"
    empty.mkdir()
    with patch("core.platform_paths.kicad_config_parent", return_value=empty):
        with pytest.raises(ValueError, match="No KiCad config folder"):
            resolve_kicad_common_dir(PLATFORM_LINUX)


def test_resolve_with_explicit_version(tmp_path):
    path, ver = resolve_kicad_common_dir(PLATFORM_LINUX, "9.0")
    assert ver == "9.0"
