# Getting Started

## 1. Run Setup

From the SpecGen application folder:

```
python setup.py
```

This detects your platform, creates a `.venv`, installs dependencies,
locates `kicad-cli`, and writes the local configuration file.

## 2. Configure kicad-cli

If kicad-cli was not found automatically, use:

**Edit → Configure kicad-cli...**

Browse to the kicad-cli executable and click **Check** to verify it works.

## 3. Open the Configure Tab

**Edit → Configure** to open the Configure tab.

Check the **Local Machine** subtab to verify your KSG_* tokens resolve
correctly. Check the **Validation** subtab and run validation.

## 4. Open or Create a Project

Use **File → Open SpecGen Project...** to open an existing `.kicad_specgen`
project file.

See **Project Setup and Tokens** for token concepts.
