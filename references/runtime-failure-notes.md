# 0.1.1 — bootstrap repair after a real runtime failure

The supplied screenshot shows repeated runtime rejections of filesystem tools as not enabled, an invocation of the short agent label archive-broker that was not found/allowed, and a literal wildcard tool invocation. It also shows speculative permission/configuration explanations being repeated without evidence of a changed configuration.

## What the package changes

- The primary and workflow now contain an explicit lookup table from role label to declared agent identity. The expected broker is sfl-strata-archive-broker; a runtime-qualified identity must be confirmed from its actual roster.
- An initial archive_status tool checks version, configured roots and optional capability flags without collecting data. No generic filesystem MCP server is required.
- list_archive_directory supports a simple nonrecursive, bounded metadata listing inside configured roots, including non-note files. It does not need content mode or start an archive-wide inventory.
- Both bundled MCP servers explicitly list exact enabledTools and eagerly register their schemas using tools.<name>.eager and antigravity/alwaysLoad metadata. These are registration settings, not blanket permission grants.
- Both operative prompts require stopping a failed binding branch rather than retrying different punctuation, wildcard tools, unrelated servers or unverified permission instructions. This is a prompt requirement, not a hard runtime execution guard.
- diagnose.py separates package declarations, MCP registration settings, direct stdio service behavior, configured root scope, native validation and actual roster output. It does not change settings, inspect global MCP credentials, scan notes or claim a direct stdio result proves agent-level invocation.
- The project installer supports --upgrade with a backup outside plugin discovery and preserves the installed config/workstation.json. Existing global/workspace filesystem MCP settings are not modified. User edits to old agent files remain in the backup; the new package installs its corrected profiles.

## Observed versus unresolved

The original package's short role references were insufficiently explicit for reliable invocation. The screenshot also demonstrates tool-enablement rejection; it does not establish whether the installed server allowlist, custom-agent tool scope, inheritance, or a CLI defect caused it. File read scope and approval rules are separate from tool registration. A wildcard permission pattern is not a callable tool identity.

The official repository has user reports of MCP discovery succeeding while calls fail as not enabled (issues 39 and 71). Those reports concern other environments and do not prove this Linux session has the same cause. The 0.1.1 eager registration change uses documented interfaces; it is not asserted to fix every runtime enablement failure.

## Validation performed

Antigravity CLI 1.5.3 was downloaded from the official installer-linked release manifest into scratch and verified against its SHA-512. Its native strict validator accepted this package with 12 agents, 2 skills and 2 MCP servers. No global CLI installation or authenticated model execution was performed. A separate native agent-list attempt returned success with empty output; that was NOT counted as successful broker discovery. The diagnostic treats missing expected roster text as unresolved even when exit status is zero.

The new status/listing/eager-registration/upgrade diagnostics have fixture and real stdio subprocess tests. Effective MCP availability and child invocation inside the user's running agent context still need verification on that machine. The user's screenshot does not expose the CLI version or complete effective configuration.

Official references consulted:
- https://antigravity.google/docs/mcp?tab=cli — server enabledTools/disabledTools and eager schemas
- https://antigravity.google/docs/subagents?tab=cli — custom agent names, tools and discovery
- https://github.com/google-antigravity/antigravity-cli/issues/39
- https://github.com/google-antigravity/antigravity-cli/issues/71
