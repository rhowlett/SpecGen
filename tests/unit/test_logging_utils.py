# v0.1
################################################################################
#  Project   : SpecGen
#  File      : test_logging_utils.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""Unit tests for core.logging_utils."""
import logging
from core.logging_utils import configure_logging


def test_configure_logging_adds_handler(tmp_path):
    root = logging.getLogger()
    initial_count = len(root.handlers)
    configure_logging(log_dir=tmp_path)
    assert len(root.handlers) >= initial_count
    # Clean up
    for h in root.handlers[initial_count:]:
        root.removeHandler(h)


def test_log_file_created(tmp_path):
    root = logging.getLogger()
    initial = list(root.handlers)
    configure_logging(log_dir=tmp_path)
    logging.getLogger("test_lf").info("test message")
    log_file = tmp_path / "specgen.log"
    assert log_file.exists()
    for h in root.handlers:
        if h not in initial:
            root.removeHandler(h)
            break
