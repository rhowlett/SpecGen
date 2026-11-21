# v0.1
################################################################################
#                                                                              #
# ███████  ███████    ██ ███████  ██   ██     ███████  ██   ██    ██ ███████   #
# ██   ██  ██   ██    ██ ██   ██  ██   ██     ██   ██  ██   ██    ██ ██   ██   #
# ██   ██  ██   ██    ██ ██       ██ ██       ██       ██   ██    ██ ██   ██   #
# ████████ ████████  ███ ███      ████████    ███      ████████  ███ ███████   #
# ███  ███ ███  ███  ███ ███      ███  ███    ███      ███  ███  ███ ███       #
# ███  ███ ███  ███  ███ ███      ███  ███    ███      ███  ███  ███ ███       #
# ███  ███ ███  ███  ███ ███  ███ ███  ███    ███  ███ ███  ███  ███ ███       #
# ████████ ███  ███  ███ ████████ ███  ███    ████████ ███  ███  ███ ███       #
#                                                                              #
################################################################################
#  Project   : SpecGen
#  File      : app.py
#  Copyright : (c) 2026 brickChip and Richard Howlett. All rights reserved.
#  Author    : Richard Howlett <rhowlett@eenerd.com>
#  License   : PolyForm Noncommercial 1.0.0. Free for noncommercial use;
#              commercial use requires written permission from the owner.
#              Full terms in LICENSE at the project root.
#  Warranty  : None. Provided as is; the owner is not liable for any
#              damages arising from its use (No Liability, LICENSE).
#  BRICKCHIP-ENTRY-POINT: Launch the SpecGen GUI
#  SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
################################################################################

"""
app.py — Application bootstrap.

Instantiation order matters:
  1. configure_logging + get_qt_handler (before any other objects log)
  2. QApplication
  3. AppState
  4. ConfigService, ValidationService
  5. MainWindow

app_state, config_service, and validation_service are injected by reference.
Nothing is a global module-level variable.
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.logging_utils import configure_logging, get_qt_handler
from core.app_state import AppState
from core.platform_paths import detect_platform, resolve_kicad_common_dir
from services.config_service import ConfigService
from services.validation_service import ValidationService
from ui.main_window import MainWindow
from ui import theme as theme_mod

log = logging.getLogger(__name__)


def main() -> int:
    # --- 1. Logging (must be first) ---
    configure_logging(console_level=logging.DEBUG)
    log.info("KiCad SpecGen starting")

    # --- 2. QApplication ---
    app = QApplication(sys.argv)
    app.setApplicationName("KiCad SpecGen")
    app.setOrganizationName("KiCad SpecGen Contributors")

    # --- 3. Qt log handler (after QApplication exists) ---
    get_qt_handler()

    # --- 4. AppState + services ---
    app_state = AppState()
    config_service    = ConfigService(app_state)
    validation_service = ValidationService(app_state)

    # --- 5. Locate and load local config ---
    platform = detect_platform()
    try:
        kicad_common, version = resolve_kicad_common_dir(platform)
    except ValueError as e:
        log.warning("KICAD_COMMON_DIR not found: %s", e)
        kicad_common = Path.home() / ".config" / "kicad" / "9.0"

    local_config_path = kicad_common / "kicad_specgen_local.json"

    if local_config_path.exists():
        try:
            config_service.load_all(local_config_path)
        except Exception as e:
            log.warning("Failed to load config: %s", e)
    else:
        log.warning("Local config not found: %s — setup required", local_config_path)

    # --- 6. Apply theme before showing window ---
    theme_name = "dark"
    if app_state.local_config:
        theme_name = app_state.local_config.theme
    theme_mod.apply_theme(theme_name)

    # --- 7. Main window ---
    window = MainWindow(app_state, config_service, validation_service)

    # Restore geometry
    if app_state.local_config:
        geo = app_state.local_config.last_session.get("window_geometry", {})
        if geo.get("width") and geo.get("height"):
            window.setGeometry(
                geo.get("x", 100), geo.get("y", 100),
                geo["width"], geo["height"]
            )

    window.show()
    log.info("MainWindow shown")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
