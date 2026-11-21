# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_validators.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Unit tests for core.validators."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.validators import (validate_local_config, validate_company_config,
                              validate_users_config, ValidationReport)
from core.specgen_local_config import LocalConfig


def _make_local(tokens=None, tools=None, preferences=None):
    cfg = LocalConfig()
    cfg.tokens = tokens or {
        "KSG_APP_DIR": "/app",
        "KSG_SYSTEM_CONFIG_DIR": "/cfg",
        "KSG_COMPANY_DIR": "/co",
        "KSG_COMPANY_SPECGEN_DIR": "/co/specgen",
        "KSG_COMPANY_COMMON_DIR": "/co/common",
        "KSG_USER_SPECGEN_DIR": "/user/specgen",
        "KSG_USER_COMMON_DIR": "/user/common",
    }
    cfg.tools = tools or {}
    cfg.preferences = preferences or {"theme": "dark"}
    return cfg


def test_writable_token_inside_app_dir_fails():
    """A writable token inside KSG_APP_DIR must fail validation."""
    cfg = _make_local(tokens={
        "KSG_APP_DIR": "/app",
        "KSG_SYSTEM_CONFIG_DIR": "/cfg",
        "KSG_COMPANY_DIR": "/co",
        "KSG_COMPANY_SPECGEN_DIR": "/co/specgen",
        "KSG_COMPANY_COMMON_DIR": "/co/common",
        "KSG_USER_SPECGEN_DIR": "/app/SpecGen/Users/default",  # inside APP_DIR!
        "KSG_USER_COMMON_DIR": "/user/common",
    })
    results = validate_local_config(cfg, cfg.tokens)
    user_specgen = [r for r in results if r.check_id == "token_ksg_user_specgen_dir"]
    assert user_specgen and user_specgen[0].status == "fail"
    assert "KSG_APP_DIR" in user_specgen[0].message


def test_empty_writable_token_warns_not_fails():
    """An empty writable token is 'not configured' (warn), not a hard fail."""
    cfg = _make_local(tokens={
        "KSG_APP_DIR": "/app",
        "KSG_SYSTEM_CONFIG_DIR": "/cfg",
        "KSG_COMPANY_DIR": "/co",
        "KSG_COMPANY_SPECGEN_DIR": "",
        "KSG_COMPANY_COMMON_DIR": "",
        "KSG_USER_SPECGEN_DIR": "",
        "KSG_USER_COMMON_DIR": "",
    })
    results = validate_local_config(cfg, cfg.tokens)
    for cid in ("token_ksg_user_specgen_dir", "token_ksg_company_common_dir"):
        r = [x for x in results if x.check_id == cid]
        assert r and r[0].status == "warn"


def test_required_tokens_all_present():
    cfg = _make_local()
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.is_absolute", return_value=True):
        results = validate_local_config(cfg, cfg.tokens)
    statuses = {r.check_id: r.status for r in results}
    for tok in ("token_ksg_app_dir", "token_ksg_company_dir"):
        assert statuses.get(tok) in ("pass", "warn")


def test_missing_token_fails():
    cfg = LocalConfig()
    cfg.tokens = {}
    cfg.tools = {}
    cfg.preferences = {"theme": "dark"}
    results = validate_local_config(cfg, {})
    fails = [r for r in results if r.status == "fail"]
    assert len(fails) > 0


def test_company_config_no_environments():
    from core.specgen_company_config import CompanyConfig
    cfg = CompanyConfig(environments={})
    results = validate_company_config(cfg)
    warns = [r for r in results if r.status == "warn"]
    assert any("environment" in r.check_id for r in warns)


def test_validation_report_overall():
    from core.validators import ValidationResult
    report = ValidationReport()
    report.results.append(ValidationResult("a", "pass", "ok"))
    assert report.overall == "pass"
    report.results.append(ValidationResult("b", "warn", "warning"))
    assert report.overall == "warn"
    report.results.append(ValidationResult("c", "fail", "error"))
    assert report.overall == "fail"
