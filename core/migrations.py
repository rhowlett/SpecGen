# v0.1
################################################################################
#  Project   : SpecGen
#  File      : migrations.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""
migrations.py — Schema version detection and migration.

Must Not Do: No file I/O. Pure data transforms.
"""
from __future__ import annotations
import logging
log = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1

REQUIRED_LOCAL_TOKENS = [
    "KSG_APP_DIR", "KSG_SYSTEM_CONFIG_DIR", "KSG_COMPANY_DIR",
    "KSG_COMPANY_SPECGEN_DIR", "KSG_COMPANY_COMMON_DIR",
    "KSG_USER_SPECGEN_DIR", "KSG_USER_COMMON_DIR",
]

# Tokens that must point to a user-writable location. A writable token whose
# path falls inside KSG_APP_DIR is invalid (the app never writes to APP_DIR).
WRITABLE_SPACE_TOKENS = [
    "KSG_COMPANY_SPECGEN_DIR", "KSG_COMPANY_COMMON_DIR",
    "KSG_USER_SPECGEN_DIR", "KSG_USER_COMMON_DIR",
]

PROTECTED_TOKENS = frozenset({
    "SPECGEN_PROJECT_FILE", "KSG_PROJECT_SPECGEN_DIR",
    "KICAD_PROJECT_DIR", "GIT_PROJECT_DIR",
    "JOBSET_OUTPUT_DIR", "FAB_OUTPUT_DIR",
})


def get_schema_version(data: dict) -> int:
    v = data.get("schema_version")
    if v is None:
        log.warning("schema_version missing — treating as version 1.")
        return 1
    return int(v)


def migrate_local_config(data: dict) -> dict:
    v = get_schema_version(data)
    if v == CURRENT_SCHEMA_VERSION:
        return data
    log.warning("Unknown schema_version %s in local config — loading as-is.", v)
    return data


def migrate_company_config(data: dict) -> dict:
    v = get_schema_version(data)
    if v == CURRENT_SCHEMA_VERSION:
        return data
    log.warning("Unknown schema_version %s in company config — loading as-is.", v)
    return data


def migrate_users_config(data: dict) -> dict:
    v = get_schema_version(data)
    if v == CURRENT_SCHEMA_VERSION:
        return data
    log.warning("Unknown schema_version %s in users config — loading as-is.", v)
    return data
