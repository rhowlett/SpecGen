# KiCad SpecGen — GUI Theme Specification

> **Document role:** Normative reference for the SpecGen application theme
> system. Defines available themes, colour palettes, QSS implementation
> guidance, and the `preferences.theme` enum values stored in
> `kicad_specgen_local.json`.
> **Authority:** This document. All theme-related values in other documents
> must match what is defined here.
> **Companion documents:** `SpecGen_GUI_Menus.md` (Theme submenu),
> `SpecGen_Schema_Definitions.md` (preferences schema),
> `SpecGen_Stage_Plan.md` (Stage 1 implementation).
> **Living document policy:** Update this document when new themes are added,
> palette values are adjusted, or QSS implementation details change. Update
> `SpecGen_Schema_Definitions.md` `preferences.theme` enum in parallel.
> **Status:** Stage 0 — specification complete. Implementation in Stage 1.

---

## 1. Theme Overview

SpecGen provides six themes selectable from `View → Theme`. The active theme
is stored in `kicad_specgen_local.json → preferences.theme` and takes effect
immediately without restarting.

| Theme ID | Display Name | Description |
|---|---|---|
| `system` | System | Follows the OS light/dark mode setting. Resolves to Light or Dark at runtime. |
| `light` | Light | Clean light background. Standard for documentation-focused work. |
| `dark` | Dark | Dark background. Reduces eye strain in low-light environments. |
| `engineering_dark` | Engineering Dark | High-contrast dark theme. Inspired by PCB/EDA tool conventions. Coloured text for status and log levels. |
| `ion_dark` | ION Dark | ION brand palette — deep tech aesthetic. Obsidian Coal background, Electric Cyan accents. |
| `ion_light` | ION Light | ION brand palette — clean corporate variant. Clean Frost background, Corporate Blue accents. |

**Minimum requirement:** Light and Dark must both be fully implemented in
Stage 1. System, Engineering Dark, ION Dark, and ION Light are
implemented in Stage 1 if time permits; otherwise they fall back to Dark.
All six names appear in the Theme submenu from Stage 1 onwards.

---

## 2. Colour Palette

All colours are defined as CSS custom properties on `:root` so that QSS
stylesheets and any embedded HTML (e.g. help viewer) can reference them
consistently. The QSS layer reads these via `theme.py` constants and
substitutes them into the stylesheet template.

### 2.1 Palette Token Names

The following token names are used throughout `theme.py` and the QSS
template. Each theme provides a value for every token.

```text
Background tokens
  --bg-primary            Main window and panel background
  --bg-secondary          Sidebar, tab bar, toolbar background
  --bg-tertiary           Input fields, table cells, code blocks
  --bg-hover              Hovered item background (buttons, list items)
  --bg-selected           Selected item background (list, table row, tab)
  --bg-disabled           Disabled widget background

Text tokens
  --text-primary          Primary body text
  --text-secondary        Labels, captions, placeholder text
  --text-disabled         Disabled widget text
  --text-inverse          Text on accent/selected backgrounds
  --text-link             Hyperlinks in help viewer

Border tokens
  --border-primary        Default widget borders, separators
  --border-focus          Focused widget border (keyboard focus ring)
  --border-input          Input field border (unfocused)
  --border-input-active   Input field border (focused)

Accent tokens
  --accent-primary        Primary action buttons, active tab indicator
  --accent-hover          Hovered primary button
  --accent-pressed        Pressed primary button

Save-state button tokens
  --save-dirty-bg         Save button background when there are unsaved changes (green)
  --save-dirty-hover      Hovered dirty Save button
  --save-dirty-text       Text/foreground on the dirty Save button (contrast-checked)

Section heading token (specgen_section_heading)
  --section-heading-color Section heading text colour (e.g. "kicad-cli Information")
  --section-heading-size  Section heading font size in points (default 13)
  --section-heading-weight Section heading font weight (default 600/DemiBold)

Shared input sizing tokens (apply to ALL themes — not per-theme)
  input_min_height        Minimum height in px for text boxes, dropdowns, and
                          spin boxes (default 28). Gives the font vertical room
                          so text is not clipped.
  input_v_padding         Top/bottom padding in px for the same widgets
                          (default 4). Keeps ascenders/descenders clear.

Status tokens
  --status-ok             ✓ Pass indicators, success badges
  --status-warning        ⚠ Warning indicators, non-blocking issues
  --status-error          ✗ Error indicators, blocking issues
  --status-info           Informational badges, neutral status

Sidebar tokens
  --sidebar-bg            Sidebar background
  --sidebar-item-text     Sidebar navigation label text
  --sidebar-selected-bg   Active sidebar item background
  --sidebar-selected-text Active sidebar item text
  --sidebar-separator     Sidebar separator line colour

Log/Output tokens (used in Output Log and Logs tab)
  --log-bg                Log viewer background
  --log-text              Default log entry text
  --log-info              INFO level entries
  --log-warning           WARNING level entries
  --log-error             ERROR level entries
  --log-success           Success / ✓ completion entries
  --log-timestamp         Timestamp prefix text
  --log-destination       Destination name in jobset output

Wireframe box tokens (used in wireframe preview if ever rendered)
  --wf-border             Wireframe box border colour
  --wf-text               Wireframe content text colour
```

---

### 2.2 Light Theme

```text
Theme ID: light
Display Name: Light

Background
  --bg-primary:            #FFFFFF
  --bg-secondary:          #F5F5F5
  --bg-tertiary:           #FAFAFA
  --bg-hover:              #E8E8E8
  --bg-selected:           #D0E4F7
  --bg-disabled:           #EFEFEF
   
Text
  --text-primary:          #1A1A1A
  --text-secondary:        #5A5A5A
  --text-disabled:         #AAAAAA
  --text-inverse:          #FFFFFF
  --text-link:             #0066CC

Border
  --border-primary:        #D0D0D0
  --border-focus:          #0078D4
  --border-input:          #BBBBBB
  --border-input-active:   #0078D4

Accent
  --accent-primary:        #0078D4
  --accent-hover:          #106EBE
  --accent-pressed:        #005A9E

Status
  --status-ok:             #107C10
  --status-warning:        #D17A00
  --status-error:          #C42B1C
  --status-info:           #0078D4

Sidebar
  --sidebar-bg:            #F0F0F0
  --sidebar-item-text:     #2A2A2A
  --sidebar-selected-bg:   #D0E4F7
  --sidebar-selected-text: #003580
  --sidebar-separator:     #C8C8C8

Log/Output
  --log-bg:                #FAFAFA
  --log-text:              #1A1A1A
  --log-info:              #1A1A1A
  --log-warning:           #7A4400
  --log-error:             #C42B1C
  --log-success:           #107C10
  --log-timestamp:         #777777
  --log-destination:       #0066CC
```

---

### 2.3 Dark Theme

```text
Theme ID: dark
Display Name: Dark

Background
  --bg-primary:            #1E1E1E
  --bg-secondary:          #252526
  --bg-tertiary:           #2D2D2D
  --bg-hover:              #3A3A3A
  --bg-selected:           #094771
  --bg-disabled:           #2A2A2A

Text
  --text-primary:          #D4D4D4
  --text-secondary:        #9D9D9D
  --text-disabled:         #555555
  --text-inverse:          #FFFFFF
  --text-link:             #4EC9FF

Border
  --border-primary:        #3C3C3C
  --border-focus:          #007ACC
  --border-input:          #3C3C3C
  --border-input-active:   #007ACC

Accent
  --accent-primary:        #007ACC
  --accent-hover:          #1A8FD1
  --accent-pressed:        #005F9E

Status
  --status-ok:             #4EC994
  --status-warning:        #FFB84D
  --status-error:          #F14C4C
  --status-info:           #4EC9FF

Sidebar
  --sidebar-bg:            #252526
  --sidebar-item-text:     #CCCCCC
  --sidebar-selected-bg:   #094771
  --sidebar-selected-text: #FFFFFF
  --sidebar-separator:     #3C3C3C

Log/Output
  --log-bg:                #1A1A1A
  --log-text:              #D4D4D4
  --log-info:              #D4D4D4
  --log-warning:           #FFB84D
  --log-error:             #F14C4C
  --log-success:           #4EC994
  --log-timestamp:         #666666
  --log-destination:       #4EC9FF
```

---

### 2.4 Engineering Dark Theme

Inspired by PCB/EDA tool conventions: very dark background, high-contrast
coloured text for different content types, green-on-dark for terminal-style
output. Familiar to KiCad users.

```text
Theme ID: engineering_dark
Display Name: Engineering Dark

Background
  --bg-primary:            #0D0D0D
  --bg-secondary:          #141414
  --bg-tertiary:           #1A1A1A
  --bg-hover:              #222222
  --bg-selected:           #1A3A1A
  --bg-disabled:           #161616

Text
  --text-primary:          #E0E0E0
  --text-secondary:        #888888
  --text-disabled:         #444444
  --text-inverse:          #000000
  --text-link:             #66CCFF

Border
  --border-primary:        #2A2A2A
  --border-focus:          #33AA33
  --border-input:          #333333
  --border-input-active:   #33AA33

Accent
  --accent-primary:        #2D8C2D
  --accent-hover:          #3AAA3A
  --accent-pressed:        #1E6B1E

Status
  --status-ok:             #33CC33
  --status-warning:        #CCAA00
  --status-error:          #CC3333
  --status-info:           #33AACC

Sidebar
  --sidebar-bg:            #0A0A0A
  --sidebar-item-text:     #BBBBBB
  --sidebar-selected-bg:   #1A3A1A
  --sidebar-selected-text: #33CC33
  --sidebar-separator:     #222222

Log/Output
  --log-bg:                #050505
  --log-text:              #CCCCCC
  --log-info:              #CCCCCC
  --log-warning:           #CCAA00
  --log-error:             #CC3333
  --log-success:           #33CC33
  --log-timestamp:         #555555
  --log-destination:       #66CCFF
```

---

### 2.5 ION Dark Theme

Based on ION's brand aesthetic — deep tech, high-contrast dark style.
Source brand values: Electric Cyan #00D4FF (primary accent), Deep Cobalt
#004F77 (secondary/hover), ION Navy #16295F (selection/pressed),
ION Gold #F6C844 (warning/secondary accent), Obsidian Coal #0B0F12
(background), Dark Slate #161F26 (surface), Absolute White #FFFFFF
(text primary), Muted Ice #98A6B0 (text secondary).

Brand colour notes:
- #16295F ION Navy — deep brand navy, luminance 0.022. Used for
  selection backgrounds to distinguish from the Electric Cyan accent.
  Contrast of Electric Cyan on Navy: ≈ 8.3:1 — passes WCAG AA.
- #F6C844 ION Gold — warm brand gold, luminance 0.619. Used as
  warning indicator and secondary accent. Gold on Obsidian Coal: ≈ 9.1:1 —
  passes WCAG AAA. Do not use Gold as text on white backgrounds (fails AA).

```text
Theme ID: ion_dark
Display Name: ION Dark

Background
  --bg-primary:            #0B0F12   Obsidian Coal — main canvas
  --bg-secondary:          #161F26   Dark Slate — sidebar, tab bar, panels
  --bg-tertiary:           #1C2830   Input fields, table cells, code blocks
  --bg-hover:              #1E3040   Hovered list items and buttons
  --bg-selected:           #16295F   ION Navy — selected rows, active tab
  --bg-disabled:           #131719   Disabled widget fill

Text
  --text-primary:          #FFFFFF   Absolute White — headings, body text
  --text-secondary:        #98A6B0   Muted Ice — labels, captions, placeholders
  --text-disabled:         #3D4F5A   Greyed-out disabled text
  --text-inverse:          #0B0F12   Dark text on cyan/gold accent backgrounds
  --text-link:             #00D4FF   Electric Cyan — hyperlinks

Border
  --border-primary:        #1E3040   Subtle widget borders and separators
  --border-focus:          #00D4FF   Electric Cyan — keyboard focus ring
  --border-input:          #263545   Input field border (unfocused)
  --border-input-active:   #00D4FF   Electric Cyan — focused input border

Accent
  --accent-primary:        #00D4FF   Electric Cyan — primary buttons, active indicators
  --accent-hover:          #004F77   Deep Cobalt — hovered primary button
  --accent-pressed:        #16295F   ION Navy — pressed primary button

Status
  --status-ok:             #00D4A0   Cyan-tinted green — readable on Obsidian Coal
  --status-warning:        #F6C844   ION Gold — brand warning colour
  --status-error:          #FF4D4D   Clear red — error indicator
  --status-info:           #00D4FF   Electric Cyan — informational badge

Sidebar
  --sidebar-bg:            #0B0F12   Obsidian Coal (matches bg-primary)
  --sidebar-item-text:     #98A6B0   Muted Ice
  --sidebar-selected-bg:   #16295F   ION Navy — selected item background
  --sidebar-selected-text: #00D4FF   Electric Cyan — active item label
  --sidebar-separator:     #1E3040   Subtle separator line

Log/Output
  --log-bg:                #080B0D   Near-black — slightly darker than bg-primary
  --log-text:              #C8D4DA   Slightly brighter than text-secondary
  --log-info:              #C8D4DA   Default log text colour
  --log-warning:           #F6C844   ION Gold — brand warning
  --log-error:             #FF4D4D   Clear red
  --log-success:           #00D4A0   Cyan-tinted green
  --log-timestamp:         #3D5A6A   Dim timestamp prefix
  --log-destination:       #00D4FF   Electric Cyan — destination name highlight
```

---

### 2.6 ION Light Theme

ION brand adapted to a clean, high-accessibility light variant.
Source brand values: Corporate Blue #007CA3 (primary accent), Sky Cyan
tint #E0F7FC (hover), ION Navy #16295F (deep accent/text-inverse),
ION Gold #F6C844 (warning accent), Clean Frost #F4F7F9 (background),
Solid White #FFFFFF (surface/inputs), Deep Charcoal #0B0F12 (text
primary), Slate Gray #556470 (text secondary).

Brand colour notes:
- #16295F ION Navy — used as `--text-inverse` (text on Corporate Blue
  buttons) and `--accent-pressed`. Provides stronger brand identity than
  generic white-on-blue. Contrast on Corporate Blue #007CA3: ≈ 4.8:1 —
  passes WCAG AA for large text. Contrast on Clean Frost: ≈ 10.3:1 — AAA.
- #F6C844 ION Gold — used as `--status-warning` background fill (not
  as text on white). Dark text (#0B0F12) on Gold: ≈ 9.1:1 — AAA. Do not
  render Gold text on white background (contrast only 2.4:1 — fails AA).

```text
Theme ID: ion_light
Display Name: ION Light

Background
  --bg-primary:            #F4F7F9   Clean Frost — main canvas
  --bg-secondary:          #EAF0F4   Slightly deeper frost — sidebar, tab bar
  --bg-tertiary:           #FFFFFF   Solid White — input fields, table cells
  --bg-hover:              #E0F7FC   Sky Cyan tint — hovered items
  --bg-selected:           #B8EBF5   Deeper sky cyan — selected rows, active tab
  --bg-disabled:           #EEF1F3   Disabled widget fill

Text
  --text-primary:          #0B0F12   Deep Charcoal — main body text
  --text-secondary:        #556470   Slate Gray — labels, captions
  --text-disabled:         #AAB4BC   Greyed-out disabled text
  --text-inverse:          #16295F   ION Navy — text on accent (Corporate Blue) backgrounds
  --text-link:             #007CA3   Corporate Blue — hyperlinks

Border
  --border-primary:        #D0DAE0   Soft separator borders
  --border-focus:          #007CA3   Corporate Blue — keyboard focus ring
  --border-input:          #BCC7CE   Input field border (unfocused)
  --border-input-active:   #007CA3   Corporate Blue — focused input border

Accent
  --accent-primary:        #007CA3   Corporate Blue — primary buttons
  --accent-hover:          #006A8C   Slightly deeper on hover
  --accent-pressed:        #16295F   ION Navy — pressed primary button

Status
  --status-ok:             #0A7A2A   Deep green — readable on Clean Frost
  --status-warning:        #7A5000   Dark gold-derived amber (Gold as bg fill; this for text)
  --status-error:          #C42B1C   Deep red — error indicator
  --status-info:           #007CA3   Corporate Blue — informational badge

Sidebar
  --sidebar-bg:            #EAF0F4   Slightly deeper frost
  --sidebar-item-text:     #2A3840   Dark text on light sidebar
  --sidebar-selected-bg:   #B8EBF5   Deeper sky cyan
  --sidebar-selected-text: #16295F   ION Navy — active item label on cyan background
  --sidebar-separator:     #C8D5DC   Subtle separator

Log/Output
  --log-bg:                #FFFFFF   Solid White — clean log background
  --log-text:              #0B0F12   Deep Charcoal
  --log-info:              #0B0F12   Default log text
  --log-warning:           #7A5000   Dark gold-derived amber — readable on white
  --log-error:             #C42B1C   Deep red
  --log-success:           #0A7A2A   Deep green
  --log-timestamp:         #778B96   Mid-tone timestamp
  --log-destination:       #007CA3   Corporate Blue — destination name highlight
```

**Note on Gold in ION Light:** #F6C844 is used as a background fill
for warning badges and indicators (e.g. `⚠` icon background), with
#0B0F12 Deep Charcoal as the text on top. It is not used as text colour
on white or frost backgrounds. `--status-warning` above is the dark
gold-derived text value for inline warning text.

---

### 2.7 System Theme

The System theme is a runtime alias. It does not have its own palette.
At startup, the application queries the OS for the current light/dark mode
and resolves to either the Light or Dark palette.

```text
Theme ID: system
Display Name: System

Resolution:
  OS reports dark mode  → use Dark palette
  OS reports light mode → use Light palette
  OS detection fails    → fall back to Dark palette

PySide6 detection:
  QStyleHints().colorScheme() == Qt.ColorScheme.Dark → Dark
  else                                                → Light
```

---

## 3. `preferences.theme` Enum Values

The value stored in `kicad_specgen_local.json → preferences.theme` must be
one of the following strings:

```text
"system"            → System (OS-adaptive)
"light"             → Light
"dark"              → Dark
"engineering_dark"  → Engineering Dark
"ion_dark"       → ION Dark
"ion_light"      → ION Light
```

Default when `preferences.theme` is absent or unrecognised: `"dark"`.

These values are the authoritative enum for the `preferences` schema in
`SpecGen_Schema_Definitions.md` §2.

---

## 4. `theme.py` Implementation Guidance

`ui/theme.py` is responsible for:

```text
1. Reading preferences.theme from app_state (loaded from kicad_specgen_local.json)
2. Resolving "system" to "light" or "dark" using QStyleHints
3. Loading the palette constants for the resolved theme
4. Substituting palette constants into the QSS template string
5. Applying the resulting QSS via QApplication.setStyleSheet()
6. Emitting a theme_changed signal so any widgets that need manual updates
   can respond (e.g. custom-painted widgets, log viewers)
```

### QSS template approach

Rather than maintaining separate `.qss` files per theme, `theme.py` maintains
a single parameterised QSS template string with placeholders:

```python
QSS_TEMPLATE = """
QMainWindow, QDialog {{
    background-color: {bg_primary};
    color: {text_primary};
}}

QListWidget {{
    background-color: {bg_secondary};
    color: {text_primary};
    border: 1px solid {border_primary};
}}

QListWidget::item:selected {{
    background-color: {bg_selected};
    color: {text_inverse};
}}
...
"""
```

Palette constants are substituted at runtime:

```python
def apply_theme(theme_id: str, app: QApplication) -> None:
    palette = PALETTES[resolve_theme(theme_id)]
    qss = QSS_TEMPLATE.format(**palette)
    app.setStyleSheet(qss)
```

### Theme change at runtime

When the user selects a new theme from `View → Theme`:

```text
1. Write new theme ID to preferences.theme in app_state
2. Write kicad_specgen_local.json (preferences section only)
3. Call theme.apply_theme(new_id, QApplication.instance())
4. Emit theme_changed signal
5. Force repaint of all top-level windows
```

No restart required.

---

## 5. Typography

All themes share the same font settings. Typography is not per-theme.

```text
Application font:     System default sans-serif (QApplication.font())
Monospace font:       System default monospace (used in log viewers, code blocks)
Base font size:       System default (do not hardcode a point size)
Minimum font size:    Never set below 9pt
```

Do not hardcode font families. Use the system default so the application
respects the user's OS accessibility settings.

### 5.1 Named text style: `specgen_section_heading`

A reusable section-heading style applied to in-tab section titles such as
"KiCad SpecGen Local Token Table", "kicad-cli Information", "Company",
"Departments", and "Users".

```text
specgen_section_heading
  Font weight:  --section-heading-weight  (default 600 / DemiBold)
  Font size:    base font size + 2pt       (--section-heading-size, default 13pt)
  Colour:       --section-heading-color    (defaults to --text-primary)
  Spacing:      8px top margin, 4px bottom margin
```

Implemented as a helper in `ui/theme.py`:

```python
def make_section_heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("specgenSectionHeading")
    # QSS targets QLabel#specgenSectionHeading with size/weight/colour
    return label
```

The QSS template includes:

```css
QLabel#specgenSectionHeading {
    font-size: {section_heading_size}pt;
    font-weight: {section_heading_weight};
    color: {section_heading_color};
    margin-top: 8px;
    margin-bottom: 4px;
}
```

### 5.2 Save-state button: dirty (unsaved changes) styling

When a Configure subtab has unsaved changes, its Save button turns the
theme's green save colour to signal that a save is pending. When there are no
unsaved changes the button uses the normal `--accent-primary` styling.

```text
No unsaved changes:   normal button (--accent-primary / default)
Unsaved changes:      --save-dirty-bg background, --save-dirty-text foreground
Hover (dirty):        --save-dirty-hover background
```

Implemented by toggling a dynamic property and re-polishing:

```python
def set_save_dirty(button: QPushButton, dirty: bool) -> None:
    button.setProperty("saveDirty", dirty)
    button.style().unpolish(button)
    button.style().polish(button)
```

The QSS template includes:

```css
QPushButton[saveDirty="true"] {
    background-color: {save_dirty_bg};
    color: {save_dirty_text};
}
QPushButton[saveDirty="true"]:hover {
    background-color: {save_dirty_hover};
}
```

The green and its text colour are contrast-checked per theme (the
`--save-dirty-text` token is chosen for ≥ 4.5:1 contrast against
`--save-dirty-bg`).

### 5.3 Global input sizing (text boxes, dropdowns, spin boxes)

Input widgets must give the active font enough vertical room, or descenders
and the bottom of glyphs are clipped (about a 10% loss with the default Qt
sizing). This is controlled in **one place** so it applies to every input in
the application across all six themes.

The fix lives entirely in `ui/theme.py`:

1. Two shared tokens (not per-theme) set the size:

   ```python
   _SHARED_TOKENS = {
       "input_min_height": "28",   # px — minimum widget height
       "input_v_padding":  "4",    # px — top/bottom padding
   }
   ```

2. `apply_theme()` merges these into every palette before formatting the QSS,
   so the same values are used regardless of the active theme.

3. One QSS rule in the shared template sizes all input widget classes:

   ```css
   QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
   QDateTimeEdit, QPlainTextEdit, QAbstractSpinBox {
       min-height: {input_min_height}px;
       padding-top: {input_v_padding}px;
       padding-bottom: {input_v_padding}px;
       padding-left: 4px;
       padding-right: 4px;
   }
   QComboBox QAbstractItemView::item { min-height: {input_min_height}px; }
   QComboBox::drop-down { min-height: {input_min_height}px; }
   ```

`min-height` (rather than a fixed `height`) is deliberate: it guarantees a
floor so text is never clipped, while still allowing a widget to grow if a
larger font is selected. To resize every input in the app, change
`input_min_height` / `input_v_padding` in `_SHARED_TOKENS` — no other file and
no individual widget needs editing.

---

## 6. Icon and Status Symbol Colours

Status symbols (✓ ⚠ ✗) in the validation panel, Configure tab, and Jobset
results use the `--status-*` palette tokens for their foreground colour.
They are rendered as Unicode characters in QLabel widgets, not as image icons.

```text
✓   --status-ok
⚠   --status-warning
✗   --status-error
ℹ   --status-info   (informational label, if used)
```

---

## 7. Wireframe Box Style

The wireframe-style box borders used in the setup wizard panels and the
Configure tab subtab headers use:

```text
Border characters:  ┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼
Font:               Monospace
Colour:             --wf-border (border), --wf-text (content)
```

These are rendered in QPlainTextEdit or QLabel widgets with the monospace
font applied.

---

## 8. Stage Plan

| Stage | Theme Work |
|---|---|
| Stage 1 | Implement Light and Dark fully. Implement System as OS-adaptive alias. Implement Engineering Dark as a best-effort initial pass (may be refined later). All four entries present in Theme submenu. `theme.py` module complete with palette constants and QSS template. |
| Stage 5 | Review and polish all four themes against the full application UI. Confirm all palette tokens are applied consistently across all new widgets added in Stages 2–4. |

---

## 9. Acceptance Criteria

```text
✓ View → Theme submenu shows all four options
✓ Active theme has a checkmark next to its name
✓ Selecting a theme applies it immediately without restart
✓ Selected theme is written to kicad_specgen_local.json → preferences.theme
✓ Theme is restored correctly on next application launch
✓ System theme resolves to Light on light OS, Dark on dark OS
✓ System theme falls back to Dark if OS detection fails
✓ All --bg-*, --text-*, --border-*, --accent-*, --status-*, --sidebar-*,
  and --log-* tokens are applied in the QSS stylesheet
✓ Status symbols ✓ ⚠ ✗ use the correct --status-* colours in all themes
✓ Log viewer uses --log-* colours for all log level types
✓ Sidebar uses --sidebar-* colours including the separator line
✓ Input fields show --border-input-active when focused
✓ Disabled widgets use --bg-disabled and --text-disabled
✓ theme.py emits theme_changed signal for widgets that need manual updates
✓ Typography uses system defaults — no hardcoded font families or sizes
```

---

*End of KiCad SpecGen GUI Theme Specification.*
