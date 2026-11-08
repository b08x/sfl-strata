# Historical installation notes — 0.1.2

Superseded by version 0.3.0; see ../README.md for the current wizard and shared XDG settings.

Install the extracted directory with agy plugin install /absolute/path/to/sfl-strata. The Python project-copy installer is historical only, under references/legacy. This package remains an Antigravity plugin, not a Gemini CLI extension.

The archive MCP service now initializes and reads PLUGIN_DATA/workstation.json, with bundled config/workstation.json used only as defaults if no data config exists. Existing settings win across native replacement. archive_status reports the exact configuration_file; configure.py --config updates it explicitly without scanning. Both server paths remain relative to PLUGIN_ROOT; only runtime state uses PLUGIN_DATA.

The managed directory may be replaced by Antigravity updates. Do not keep editable user settings there. No dependency installation, automatic archive scan, or global native installation was performed by this build.

An earlier project-scoped copy can shadow a native-managed copy. Identify and retain it outside plugin discovery before switching routes; preserve its archive settings for explicit migration. No automatic workspace copy removal or global setting edits are included.
