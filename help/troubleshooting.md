# Troubleshooting

## kicad-cli not found

1. Open **Edit → Configure kicad-cli...**
2. Click **Browse...** and select the kicad-cli executable.
3. Click **Check** to verify the path works.
4. Click **Save**.

## kicad_common.json not found

1. Verify KiCad is installed and has been run at least once.
2. Open **Edit → Configure** → **Local Machine** subtab.
3. Check that `KSG_SYSTEM_CONFIG_DIR` points to the correct KiCad config folder.

## Missing KSG_* token

1. Open **Edit → Local Tokens...**
2. Add the missing token with its absolute path on this machine.
3. Click **Save**.

Or use **Edit → Resolve Missing Tokens...** when a project is open.

## Invalid project .kicad_specgen location

The project file must be under a `specgen/` folder within the KiCad project
directory. Example:

```
{KICAD_PROJECT_DIR}/specgen/myproject.kicad_specgen
```

## Permission errors writing config files

Ensure `KSG_SYSTEM_CONFIG_DIR` and `KSG_COMPANY_DIR` are writable by your
user account.
