"""Unit tests for core.token_resolver."""
from pathlib import Path
from core.token_resolver import build_token_table, resolve_ref, find_missing_tokens


def test_resolve_simple():
    table = {"KSG_APP_DIR": "/home/user/app"}
    resolved, missing = resolve_ref("{KSG_APP_DIR}/core", table)
    assert resolved == "/home/user/app/core"
    assert missing == []


def test_resolve_missing_token():
    resolved, missing = resolve_ref("{MISSING_TOKEN}/path", {})
    assert "{MISSING_TOKEN}" in resolved
    assert "MISSING_TOKEN" in missing


def test_build_token_table_priority():
    """Local tokens override kicad_vars."""
    table = build_token_table(
        local_tokens={"KSG_APP_DIR": "/local/app"},
        kicad_vars={"KSG_APP_DIR": "/kicad/app"},
    )
    assert table["KSG_APP_DIR"] == "/local/app"


def test_build_token_table_runtime_highest():
    """Runtime tokens override everything."""
    table = build_token_table(
        local_tokens={"KSG_APP_DIR": "/local"},
        runtime_tokens={"KSG_APP_DIR": "/runtime"},
    )
    assert table["KSG_APP_DIR"] == "/runtime"


def test_find_missing():
    text = "path/{MISSING}/{KSG_APP_DIR}"
    table = {"KSG_APP_DIR": "/app"}
    missing = find_missing_tokens(text, table)
    assert "MISSING" in missing
    assert "KSG_APP_DIR" not in missing


# ---- tokenize_path (reverse mapping) ---------------------------------------
from core.token_resolver import tokenize_path


def test_tokenize_path_basic(tmp_path):
    company = tmp_path / "CompanyRepo"
    company.mkdir()
    logo = company / "SpecGen" / "logo.png"
    logo.parent.mkdir(parents=True)
    logo.write_text("x")
    table = {"KSG_COMPANY_DIR": str(company)}
    result, matched = tokenize_path(str(logo), table)
    assert result == "{KSG_COMPANY_DIR}/SpecGen/logo.png"
    assert matched == "KSG_COMPANY_DIR"


def test_tokenize_path_longest_wins(tmp_path):
    company = tmp_path / "co"; company.mkdir()
    specgen = company / "SpecGen"; specgen.mkdir()
    f = specgen / "x.png"; f.write_text("x")
    table = {
        "KSG_COMPANY_DIR": str(company),
        "KSG_COMPANY_SPECGEN_DIR": str(specgen),
    }
    result, matched = tokenize_path(str(f), table)
    # Longer (more specific) token directory must win
    assert matched == "KSG_COMPANY_SPECGEN_DIR"
    assert result == "{KSG_COMPANY_SPECGEN_DIR}/x.png"


def test_tokenize_path_prefer(tmp_path):
    company = tmp_path / "co"; company.mkdir()
    specgen = company / "SpecGen"; specgen.mkdir()
    f = specgen / "x.png"; f.write_text("x")
    table = {
        "KSG_COMPANY_DIR": str(company),
        "KSG_COMPANY_SPECGEN_DIR": str(specgen),
    }
    # prefer the broader token even though a longer one also matches
    result, matched = tokenize_path(str(f), table, prefer="KSG_COMPANY_DIR")
    assert matched == "KSG_COMPANY_DIR"
    assert result == "{KSG_COMPANY_DIR}/SpecGen/x.png"


def test_tokenize_path_no_match(tmp_path):
    company = tmp_path / "co"; company.mkdir()
    outside = tmp_path / "elsewhere" / "x.png"
    outside.parent.mkdir()
    outside.write_text("x")
    table = {"KSG_COMPANY_DIR": str(company)}
    result, matched = tokenize_path(str(outside), table)
    assert matched is None
    assert result == str(outside)


def test_tokenize_path_prefer_misses_falls_back(tmp_path):
    company = tmp_path / "co"; company.mkdir()
    other = tmp_path / "other"; other.mkdir()
    f = other / "x.png"; f.write_text("x")
    table = {"KSG_COMPANY_DIR": str(company), "KSG_USER_COMMON_DIR": str(other)}
    # prefer KSG_COMPANY_DIR but file is under KSG_USER_COMMON_DIR
    result, matched = tokenize_path(str(f), table, prefer="KSG_COMPANY_DIR")
    assert matched == "KSG_USER_COMMON_DIR"   # caller compares to prefer to warn


def test_tokenize_path_roundtrip(tmp_path):
    from core.token_resolver import resolve_ref
    company = tmp_path / "co"; company.mkdir()
    f = company / "a" / "b.png"; f.parent.mkdir(); f.write_text("x")
    table = {"KSG_COMPANY_DIR": str(company)}
    tokenized, _ = tokenize_path(str(f), table)
    resolved, missing = resolve_ref(tokenized, table)
    assert missing == []
    assert Path(resolved).resolve() == f.resolve()
