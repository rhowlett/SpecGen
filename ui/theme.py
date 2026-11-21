# v0.1
################################################################################
#  Project   : SpecGen
#  File      : theme.py
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
theme.py — Theme application, section headings, and save-state button styling.

Applies the active theme from app_state.local_config.theme before the main
window is shown. Supports the six themes defined in SpecGen_GUI_Theme.md and
provides helpers for the named specgen_section_heading style and the
dirty (unsaved-changes) Save button styling.
"""
from __future__ import annotations
import logging
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

log = logging.getLogger(__name__)

VALID_THEMES = {"system", "light", "dark",
                "engineering_dark", "ion_dark", "ion_light"}

# ---------------------------------------------------------------------------
# Shared sizing tokens — apply to ALL themes. Change these in ONE place to
# resize every text box, dropdown, and spin box across the whole app.
#   input_min_height : minimum widget height in px (gives text vertical room)
#   input_v_padding  : top/bottom padding in px (keeps descenders from clipping)
# These are merged into every palette at apply_theme() time.
# ---------------------------------------------------------------------------
_SHARED_TOKENS: dict[str, str] = {
    "input_min_height": "28",
    "input_v_padding":  "4",
}

# Per-theme palette subset needed for QSS. Extend with full palettes from
# SpecGen_GUI_Theme.md as needed. Each entry includes the new save-dirty and
# section-heading tokens.
_PALETTES: dict[str, dict] = {
    "light": {
        "bg_primary": "#FFFFFF", "text_primary": "#1A1A1A",
        "bg_secondary": "#F0F0F0", "bg_selected": "#0057B7",
        "text_inverse": "#FFFFFF", "border_primary": "#C8C8C8",
        "accent_primary": "#0057B7",
        "save_dirty_bg": "#1E7E34", "save_dirty_hover": "#218838",
        "save_dirty_text": "#FFFFFF",
        "section_heading_color": "#1A1A1A",
        "section_heading_size": "13", "section_heading_weight": "600",
    },
    "dark": {
        "bg_primary": "#1E1E1E", "text_primary": "#D4D4D4",
        "bg_secondary": "#252526", "bg_selected": "#0057B7",
        "text_inverse": "#FFFFFF", "border_primary": "#3C3C3C",
        "accent_primary": "#0057B7",
        "save_dirty_bg": "#2EA043", "save_dirty_hover": "#3FB950",
        "save_dirty_text": "#0D1117",
        "section_heading_color": "#E6E6E6",
        "section_heading_size": "13", "section_heading_weight": "600",
    },
    "engineering_dark": {
        "bg_primary": "#1A1D23", "text_primary": "#CDD6F4",
        "bg_secondary": "#1E2128", "bg_selected": "#89B4FA",
        "text_inverse": "#1A1D23", "border_primary": "#313244",
        "accent_primary": "#89B4FA",
        "save_dirty_bg": "#40A02B", "save_dirty_hover": "#4CB535",
        "save_dirty_text": "#11111B",
        "section_heading_color": "#CDD6F4",
        "section_heading_size": "13", "section_heading_weight": "600",
    },
    "ion_dark": {
        "bg_primary": "#0D1117", "text_primary": "#E6EDF3",
        "bg_secondary": "#161B22", "bg_selected": "#238636",
        "text_inverse": "#FFFFFF", "border_primary": "#30363D",
        "accent_primary": "#00D4FF",
        "save_dirty_bg": "#00D4A0", "save_dirty_hover": "#00E8B0",
        "save_dirty_text": "#0D1117",
        "section_heading_color": "#E6EDF3",
        "section_heading_size": "13", "section_heading_weight": "600",
    },
    "ion_light": {
        "bg_primary": "#FFFFFF", "text_primary": "#24292F",
        "bg_secondary": "#F6F8FA", "bg_selected": "#218BFF",
        "text_inverse": "#FFFFFF", "border_primary": "#D0D7DE",
        "accent_primary": "#007CA3",
        "save_dirty_bg": "#0A7A2A", "save_dirty_hover": "#0C8F31",
        "save_dirty_text": "#FFFFFF",
        "section_heading_color": "#24292F",
        "section_heading_size": "13", "section_heading_weight": "600",
    },
}

_QSS_TEMPLATE = """
QMainWindow, QWidget {{ background-color: {bg_primary}; color: {text_primary}; }}
QListWidget {{ background-color: {bg_secondary}; }}
QListWidget::item:selected {{ background-color: {bg_selected}; color: {text_inverse}; }}

/* ---- Global input sizing -------------------------------------------------
   One rule sizes every text box, dropdown, and spin box across all six
   themes. min-height (not a fixed height) plus vertical padding gives the
   font's ascenders and descenders room so text is never clipped, while still
   letting a widget grow if a larger font is used. Adjust {input_min_height}
   and {input_v_padding} in the palette to change this globally. */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
QDateTimeEdit, QPlainTextEdit, QAbstractSpinBox {{
    min-height: {input_min_height}px;
    padding-top: {input_v_padding}px;
    padding-bottom: {input_v_padding}px;
    padding-left: 4px;
    padding-right: 4px;
}}
QComboBox QAbstractItemView::item {{
    min-height: {input_min_height}px;
}}
QComboBox::drop-down {{
    min-height: {input_min_height}px;
}}

QLabel#specgenSectionHeading {{
    font-size: {section_heading_size}pt;
    font-weight: {section_heading_weight};
    color: {section_heading_color};
    margin-top: 8px;
    margin-bottom: 4px;
}}

QPushButton[saveDirty="true"] {{
    background-color: {save_dirty_bg};
    color: {save_dirty_text};
    font-weight: 600;
    border-radius: 3px;
    padding: 4px 12px;
}}
QPushButton[saveDirty="true"]:hover {{
    background-color: {save_dirty_hover};
}}
"""


def _resolve(theme_name: str) -> str:
    if theme_name == "system":
        return "dark"   # OS detection could refine this; default to dark
    if theme_name not in VALID_THEMES:
        return "dark"
    return theme_name


def apply_theme(theme_name: str) -> None:
    """Apply the named theme to the running QApplication."""
    app = QApplication.instance()
    if not app:
        return
    if theme_name not in VALID_THEMES:
        log.warning("Unknown theme '%s' — falling back to 'dark'", theme_name)
        theme_name = "dark"
    resolved = _resolve(theme_name)
    palette = _PALETTES.get(resolved, _PALETTES["dark"])
    # Merge shared sizing tokens (input heights/padding) into the palette so
    # the QSS template can reference them. Shared tokens apply to all themes.
    merged = {**_SHARED_TOKENS, **palette}
    app.setStyleSheet(_QSS_TEMPLATE.format(**merged))
    log.info("theme: %s applied", theme_name)


def make_section_heading(text: str) -> QLabel:
    """Create a QLabel styled as a specgen_section_heading."""
    label = QLabel(text)
    label.setObjectName("specgenSectionHeading")
    return label


def set_save_dirty(button: QPushButton, dirty: bool) -> None:
    """Toggle the dirty (unsaved-changes) green styling on a Save button."""
    button.setProperty("saveDirty", bool(dirty))
    style = button.style()
    if style:
        style.unpolish(button)
        style.polish(button)
