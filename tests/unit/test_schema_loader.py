"""Unit tests for core.schema_loader and the schema/ files."""
import json
from pathlib import Path

import pytest
import jsonschema
from jsonschema import Draft7Validator

from core import schema_loader
from core.schema_loader import validate, load_schema, schema_dir, SchemaError, SCHEMA_FILES

ALL = ["local", "company", "users", "project", "kicad_common"]


def test_all_schema_files_exist():
    for name, fname in SCHEMA_FILES.items():
        assert (schema_dir() / fname).exists(), f"missing schema file: {fname}"


@pytest.mark.parametrize("name", ALL)
def test_each_schema_is_valid_draft7(name):
    schema = load_schema(name)
    Draft7Validator.check_schema(schema)   # raises if the schema itself is invalid
    assert schema.get("$schema", "").endswith("draft-07/schema#")
    assert "$id" in schema


@pytest.mark.parametrize("name", ALL)
def test_each_schema_has_title(name):
    assert load_schema(name).get("title")


def test_kicad_common_is_partial_readonly():
    schema = load_schema("kicad_common")
    # partial: must allow additional properties (KiCad owns the file)
    assert schema.get("additionalProperties") is True
    assert "read-only" in schema.get("description", "").lower()


def test_unknown_schema_name_raises():
    with pytest.raises(KeyError):
        load_schema("does_not_exist")


# ---- validate() behavior ----------------------------------------------------

def test_validate_accepts_minimal_local():
    data = {"schema_version": 1, "tokens": {
        "KSG_APP_DIR": "/a", "KSG_SYSTEM_CONFIG_DIR": "/b", "KSG_COMPANY_DIR": "/c",
        "KSG_COMPANY_SPECGEN_DIR": "/d", "KSG_COMPANY_COMMON_DIR": "/e",
        "KSG_USER_SPECGEN_DIR": "/f", "KSG_USER_COMMON_DIR": "/g",
    }}
    validate("local", data)   # should not raise


def test_validate_rejects_missing_required():
    with pytest.raises(SchemaError) as exc:
        validate("local", {"schema_version": 1})   # no tokens
    assert exc.value.schema_name == "local"


def test_validate_company_minimal():
    validate("company", {"schema_version": 1, "company": {"name": "X"}})


def test_validate_users_minimal():
    validate("users", {"schema_version": 1, "users": []})


# ---- fixtures conform to their schemas -------------------------------------

FIX = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize("fixture,name", [
    ("sample_local.json", "local"),
    ("sample_company.json", "company"),
    ("sample_company_standalone.json", "company"),
    ("sample_users.json", "users"),
])
def test_fixture_conforms_to_schema(fixture, name):
    path = FIX / fixture
    if not path.exists():
        pytest.skip(f"fixture {fixture} not present")
    validate(name, json.loads(path.read_text()))
