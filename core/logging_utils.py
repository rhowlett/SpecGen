# v0.1
################################################################################
#  Project   : SpecGen
#  File      : logging_utils.py
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
logging_utils.py — Structured logging with Qt bridge.

QtLogHandler delivers records to the Qt main thread via Signal, making it
thread-safe for Stage 3 subprocess threads without any additional locking.

Instantiate via get_qt_handler() in app.py BEFORE any other objects.
Must Not Do: No GUI widget creation in this module.

Fix note: formatTime() is on logging.Formatter, NOT logging.Handler.
          We use datetime.now().strftime() directly to avoid this.
"""
from __future__ import annotations
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

_qt_handler = None


def configure_logging(log_dir: Path | None = None,
                      console_level: int = logging.DEBUG) -> None:
    """Configure root logger with optional rotating file handler."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)-24s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if not any(isinstance(h, logging.StreamHandler)
               and not isinstance(h, logging.FileHandler)
               for h in root.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch.setFormatter(fmt)
        root.addHandler(ch)
    if log_dir is not None:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            Path(log_dir) / "specgen.log",
            maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        root.addHandler(fh)


def get_qt_handler():
    """Return the singleton QtLogHandler, creating it on first call."""
    global _qt_handler
    if _qt_handler is None:
        from PySide6.QtCore import QObject, Signal

        class _QtLogHandler(logging.Handler, QObject):
            """
            Routes Python log records to the Qt main thread via Signal.

            Uses datetime.now().strftime() for timestamps — formatTime()
            is on logging.Formatter, not logging.Handler, so calling
            self.formatTime() would raise AttributeError.
            """
            record_emitted = Signal(str, str, str, str)
            # (timestamp, level, source, message)

            def __init__(self):
                logging.Handler.__init__(self)
                QObject.__init__(self)

            def emit(self, record: logging.LogRecord) -> None:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.record_emitted.emit(
                        timestamp,
                        record.levelname,
                        record.name,
                        record.getMessage(),
                    )
                except Exception:
                    self.handleError(record)

        _qt_handler = _QtLogHandler()
        _qt_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(_qt_handler)
    return _qt_handler
