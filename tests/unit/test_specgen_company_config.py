"""Unit tests for core.specgen_company_config (department/client hierarchy)."""
import pytest
from pathlib import Path
from core.specgen_company_config import load, save, create_standalone

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_load_valid(tmp_path):
    dst = tmp_path / "company.json"
    dst.write_bytes((FIXTURES / "sample_company.json").read_bytes())
    cfg = load(dst)
    assert cfg.company_name == "Acme Engineering"
    assert cfg.company_website == "https://acme.example.com"
    assert cfg.company_address.get("city") == "Springfield"


def test_no_company_id():
    """Single-company model: company_id no longer exists."""
    cfg = create_standalone.__wrapped__ if hasattr(create_standalone, "__wrapped__") else None
    # company dataclass has no company_id attribute
    from core.specgen_company_config import CompanyConfig
    c = CompanyConfig()
    assert not hasattr(c, "company_id")


def test_create_standalone_uses_name(tmp_path):
    p = tmp_path / "company.json"
    cfg = create_standalone(p, "My Company")
    assert cfg.company_name == "My Company"


def test_departments_and_teams(tmp_path):
    dst = tmp_path / "company.json"
    dst.write_bytes((FIXTURES / "sample_company.json").read_bytes())
    cfg = load(dst)
    assert cfg.department_count == 1
    assert cfg.team_count == 2
    assert cfg.department_name("hardware") == "Hardware Engineering"
    assert cfg.team_name("hardware", "power") == "Power Electronics"
    assert cfg.get_team("hardware", "rf")["name"] == "RF Design"


def test_clients_and_projects(tmp_path):
    dst = tmp_path / "company.json"
    dst.write_bytes((FIXTURES / "sample_company.json").read_bytes())
    cfg = load(dst)
    assert cfg.client_count == 1
    proj = cfg.get_project("medical", "pacemaker")
    assert proj["status"] == "active"


def test_environments_dict(tmp_path):
    dst = tmp_path / "company.json"
    dst.write_bytes((FIXTURES / "sample_company.json").read_bytes())
    cfg = load(dst)
    assert "default" in cfg.environment_ids
    assert cfg.get_environment("med")["type"] == "client"


def test_save_roundtrip(tmp_path):
    dst = tmp_path / "company.json"
    dst.write_bytes((FIXTURES / "sample_company.json").read_bytes())
    cfg = load(dst)
    cfg.departments["software"] = {"name": "Software", "teams": {}}
    save(cfg)
    reloaded = load(dst)
    assert reloaded.department_count == 2
