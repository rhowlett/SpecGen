"""Unit tests for core.file_ops."""
import json, pytest
from pathlib import Path
from core.file_ops import write_json_atomic, read_json, ensure_dir, path_exists


def test_write_json_atomic_creates_file(tmp_path):
    target = tmp_path / "test.json"
    write_json_atomic(target, {"key": "value"})
    assert target.exists()
    data = json.loads(target.read_text())
    assert data["key"] == "value"


def test_write_json_atomic_no_tmp_left(tmp_path):
    target = tmp_path / "test.json"
    write_json_atomic(target, {"a": 1})
    assert not (tmp_path / "test.json.tmp").exists()


def test_write_json_atomic_backup(tmp_path):
    target = tmp_path / "test.json"
    write_json_atomic(target, {"v": 1})
    write_json_atomic(target, {"v": 2}, backup=True)
    bak_files = list(tmp_path.glob("*.bak_*"))
    assert len(bak_files) == 1
    bak_data = json.loads(bak_files[0].read_text())
    assert bak_data["v"] == 1


def test_write_json_atomic_creates_parent(tmp_path):
    target = tmp_path / "a" / "b" / "c.json"
    write_json_atomic(target, {})
    assert target.exists()


def test_read_json(tmp_path):
    f = tmp_path / "data.json"
    f.write_text('{"x": 42}')
    assert read_json(f)["x"] == 42


def test_read_json_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_json(tmp_path / "no.json")


def test_ensure_dir(tmp_path):
    new = tmp_path / "a" / "b"
    result = ensure_dir(new)
    assert result.is_dir()


def test_path_exists_true(tmp_path):
    assert path_exists(tmp_path)


def test_path_exists_false():
    assert not path_exists("/nonexistent/path/abc")


def test_path_exists_none():
    assert not path_exists(None)
