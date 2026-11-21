# v0.1
################################################################################
#  Project   : SpecGen
#  File      : validation_service.py
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
validation_service.py — Aggregate config validation results.

Emits app_state.validation_complete with the ValidationReport.
Also returns the report directly for synchronous callers (e.g. tests).
"""
from __future__ import annotations
import logging
from core.validators import (ValidationReport, validate_local_config,
                              validate_company_config, validate_users_config)

log = logging.getLogger(__name__)


class ValidationService:
    def __init__(self, app_state) -> None:
        self._state = app_state

    def run_config_validation(self) -> ValidationReport:
        """
        Run full configuration validation.
        Emits app_state.validation_complete with the report.
        Returns the report directly for synchronous callers.
        """
        report = ValidationReport()
        state  = self._state

        if state.local_config:
            report.results.extend(
                validate_local_config(state.local_config, state.resolved_tokens)
            )
        else:
            from core.validators import ValidationResult
            report.results.append(ValidationResult(
                check_id="local_config", status="fail",
                message="Local config not loaded — run setup.",
                source="config",
            ))

        report.results.extend(validate_company_config(state.company_config))
        report.results.extend(
            validate_users_config(state.users_config, state.active_user,
                                  state.company_config)
        )

        log.info(
            "validation: %d passed, %d warnings, %d failures",
            report.passed, report.warnings, report.failures,
        )

        # Emit signal for UI subscribers (validation_panel)
        state.validation_complete.emit(report)

        return report
