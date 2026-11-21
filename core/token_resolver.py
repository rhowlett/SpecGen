# v0.1
################################################################################
#  Project   : SpecGen
#  File      : token_resolver.py
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
token_resolver.py — Build effective token table and resolve {TOKEN} references.

Priority (highest to lowest):
  1. Protected derived runtime tokens (computed, not stored)
  2. Users config resolved paths
  3. Company config resolved paths
  4. Local config KSG_* absolute paths
  5. kicad_common.json environment.vars (lowest)

Must Not Do: No file I/O beyond path existence checks. No GUI.
"""
from __future__ import annotations
import logging, re
from pathlib import Path

log = logging.getLogger(__name__)

TOKEN_REF_RE = re.compile(r"\{([A-Z0-9_]+)\}")


def build_token_table(
    local_tokens:   dict[str, str],
    kicad_vars:     dict[str, str] | None = None,
    company_paths:  dict[str, str] | None = None,
    user_paths:     dict[str, str] | None = None,
    runtime_tokens: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Merge token sources from lowest to highest priority.
    Returns the effective token table (all values are absolute paths).
    """
    table: dict[str, str] = {}
    # Layer 5 — kicad_common vars (lowest)
    if kicad_vars:
        table.update(kicad_vars)
    # Layer 4 — local KSG_* tokens
    table.update(local_tokens)
    # Layer 3 — company paths
    if company_paths:
        table.update(company_paths)
    # Layer 2 — user paths
    if user_paths:
        table.update(user_paths)
    # Layer 1 — protected derived runtime tokens (highest, not overridable)
    if runtime_tokens:
        table.update(runtime_tokens)
    return table


def resolve_ref(ref: str, table: dict[str, str]) -> tuple[str, list[str]]:
    """
    Resolve all {TOKEN_NAME} placeholders in *ref* using *table*.
    Returns (resolved_string, list_of_missing_token_names).
    """
    missing: list[str] = []

    def _replace(m: re.Match) -> str:
        name = m.group(1)
        val  = table.get(name)
        if val is None:
            missing.append(name)
            return m.group(0)   # leave placeholder intact
        return val

    resolved = TOKEN_REF_RE.sub(_replace, ref)
    return resolved, missing


def resolve_all_refs(data: dict | list | str,
                     table: dict[str, str]) -> tuple[object, list[str]]:
    """
    Recursively resolve {TOKEN} references in any dict/list/str structure.
    Returns (resolved_copy, all_missing_token_names).
    """
    all_missing: list[str] = []

    def _walk(node):
        if isinstance(node, str):
            resolved, missing = resolve_ref(node, table)
            all_missing.extend(missing)
            return resolved
        if isinstance(node, dict):
            return {k: _walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [_walk(item) for item in node]
        return node

    return _walk(data), all_missing


def find_missing_tokens(text: str, table: dict[str, str]) -> list[str]:
    """Return token names referenced in text that are not in table."""
    return [m.group(1) for m in TOKEN_REF_RE.finditer(text)
            if m.group(1) not in table]


def tokenize_path(abs_path: str,
                  table: dict[str, str],
                  prefer: str | None = None) -> tuple[str, str | None]:
    """
    Reverse of resolve_ref: replace the leading directory of *abs_path* with a
    {TOKEN} reference when it sits under one of the token directories in
    *table*.

    Returns (result, matched_token):
      - result        the tokenized string (e.g. "{KSG_COMPANY_DIR}/logo.png")
                      or the original abs_path if nothing matched.
      - matched_token the token name that matched, or None if no token covered
                      the path.

    Matching rules:
      - Only directory-prefix matches count: the path must equal a token's
        directory or be inside it (component-wise, so /foo/bar does not match
        a token pointing at /foo/ba).
      - The LONGEST matching token directory wins, so a nested token like
        KSG_COMPANY_SPECGEN_DIR is preferred over a broader KSG_COMPANY_DIR.
      - If *prefer* is given and that token matches, it is used even if another
        token would also match (the field is anchored to that token). If
        *prefer* is given but does NOT match, the result still uses the best
        general match (or the raw path) and the caller can compare
        matched_token against prefer to warn the user.
    """
    if not abs_path:
        return abs_path, None

    try:
        target = Path(abs_path).resolve()
    except (OSError, ValueError):
        return abs_path, None

    def _rel_under(token_name: str) -> str | None:
        base = table.get(token_name)
        if not base:
            return None
        try:
            base_p = Path(base).resolve()
        except (OSError, ValueError):
            return None
        if target == base_p:
            return f"{{{token_name}}}"
        try:
            rel = target.relative_to(base_p)
        except ValueError:
            return None
        return f"{{{token_name}}}/" + rel.as_posix()

    # Honour the preferred token first.
    if prefer:
        pref_result = _rel_under(prefer)
        if pref_result is not None:
            return pref_result, prefer

    # Otherwise pick the longest-matching token directory.
    best_token: str | None = None
    best_len = -1
    for name, base in table.items():
        if not base:
            continue
        try:
            base_len = len(Path(base).resolve().parts)
        except (OSError, ValueError):
            continue
        if _rel_under(name) is not None and base_len > best_len:
            best_token, best_len = name, base_len

    if best_token is not None:
        return _rel_under(best_token), best_token   # type: ignore[return-value]

    return abs_path, None
