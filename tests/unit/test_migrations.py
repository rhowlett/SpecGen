# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_migrations.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Unit tests for core.migrations."""
from core.migrations import (get_schema_version, migrate_local_config,
                              migrate_company_config, CURRENT_SCHEMA_VERSION)


def test_get_schema_version_present():
    assert get_schema_version({"schema_version": 1}) == 1


def test_get_schema_version_missing_defaults_to_1():
    assert get_schema_version({}) == 1


def test_migrate_local_config_passthrough():
    data = {"schema_version": 1, "tokens": {}}
    result = migrate_local_config(data)
    assert result is data


def test_migrate_company_config_passthrough():
    data = {"schema_version": 1}
    assert migrate_company_config(data) is data
