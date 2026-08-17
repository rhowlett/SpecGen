# Configure Tab

Open with **Edit → Configure**.

## Local Machine Subtab

View and edit your local `KSG_*` token definitions. All values must be
absolute paths on this machine. Changes are saved per-machine and are not
shared with other users.

**kicad-cli** section shows the detected path, source, and version.
Click **Configure kicad-cli...** to change it.

## Company & User Subtab

Edit the company identity (company_id, name) and manage user profiles.
Changes are saved to the shared `kicad_specgen_company.json` and
`kicad_specgen_users.json` files.

## Environments Subtab

Set the active user and active environment for this machine. These selections
are stored locally and do not affect other users.

## Preferences Subtab

Select the active UI theme. Six themes are available:
`system`, `light`, `dark`, `engineering_dark`, `ion_dark`, `ion_light`.

## Validation Subtab

Click **Run Validation** to check your configuration. Results show:
- ✓ Pass — green (configuration is correct)
- ⚠ Warning — amber (usable but attention needed)
- ✗ Fail — red (must be resolved before project operations)
