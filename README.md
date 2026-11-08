# SFL Strata — Antigravity field notebook

**Version 0.2.0.** R.U.T.H. coordinates archaeology, stratigraphy and semantic cartography across explicitly selected archive directories. Setup now starts with a keyboard-driven Textual wizard.

## Start here

Extract the archive and launch setup from the extracted directory:

```bash
cd sfl-strata
python3 configure.py
```

The five-page wizard provides an archive folder browser, multiple roots, separate note-text/Git/current-host switches, collection budgets, a policy review and connection verification. Use Tab/Shift+Tab and Enter/Space, Ctrl+N to continue, Ctrl+P to go back, and Ctrl+Q to exit. Escape cancels the folder picker. Draft settings are written only when you choose **Save & verify**. Layouts support 80×24 and larger terminals; pages scroll when needed. True-color terminals show the archival-paper, rust and olive palette; NO_COLOR is respected.

On first use, setup prepares an isolated Python environment under `$XDG_DATA_HOME/sfl-strata/runtime` (normally `~/.local/share/sfl-strata/runtime`) if its dependencies are unavailable. This requires Python 3 with venv/pip and internet access. It installs Textual 8.2.8, jsonschema 4.x and PyYAML 6.x there. It does not alter system Python. For an offline machine, provision those dependencies in advance; the bootstrap is not an offline dependency bundle. MCP startup never downloads packages.

After verification, choose **Install plugin** to hand the reviewed directory to `agy plugin install`. Antigravity owns installation and any upgrade prompts. You can also install directly:

```bash
agy plugin install "$PWD"
agy --agent sfl-strata-coordinator
```

The install target is the extracted directory. This is an Antigravity CLI plugin with plugin.json, agents/, skills/ and bundled MCP servers. Existing installations can run configure.py in their installed plugin directory too. Reinstall the updated package and reconnect once when upgrading older MCP workers. Avoid duplicate native and historical project-scoped copies, since they can shadow one another.

## Settings and verification

The wizard and archive worker share `$XDG_CONFIG_HOME/sfl-strata/workstation.json`, normally `~/.config/sfl-strata/workstation.json`. Settings live outside the installed package and survive replacement. The native worker imports an existing `${PLUGIN_DATA}/workstation.json` only when the shared file does not exist; otherwise shipped defaults initialize it with no roots and all optional capabilities disabled. The wizard itself uses existing shared settings or bundled defaults; to import a pre-0.2 policy before first worker startup, configure the old file explicitly or let the updated worker perform its one-time migration first. Arbitrary old installations are not searched.

A running 0.2 worker validates and reloads changes before every tool request; changed policy invalidates its cached evidence. Invalid settings block collection instead of retaining old permissions. No routine restart is needed after configuring a 0.2 worker. `archive_status` reports its configuration path, policy revision and live-reload support.

**Save & verify** checks the saved revision and calls status through a fresh stdio MCP process. It separately queries private, status-only local Unix sockets belonging to already-running 0.2 workers. Matching revisions establish that those observed workers loaded the policy. “Live session not observed” is explicitly unverified; a fresh-process success does not establish that the active Antigravity agent has tools bound. If local sockets are unavailable, live status is shown as unobserved. Status sockets expose no collection operations and run only for the MCP process lifetime. No archive inventory, note contents or host observation is requested by setup.

Scriptable configuration remains available and preserves unspecified settings:

```bash
python3 configure.py --root /absolute/path/to/vault --text --git-history
python3 configure.py --no-text --max-files 1500
```

Repeat `--root` for multiple roots; `--roots` is accepted as an alias. `--config /path/workstation.json` explicitly overrides the settings file. A custom file must also be passed to the archive server with `--config`; changing only the wizard path does not retarget an existing worker. Exclusions and note extensions are shown in the wizard and remain editable in JSON. Source notes are never edited by setup or collection.

## Teams and work

| Team | Roles |
| --- | --- |
| Archaeology & Stratigraphy | Stratigraphic Chronologist, Concept Drift Analyst, Regeneration Curator |
| Semantic Cartography & Topography | Semantic Cartographer, Vector Bridge Interpreter, Friction Analyst |
| Evidence and review | Archive Broker, Author, Ideational/Interpersonal/Textual Judges, R.U.T.H. |

There are 12 profiles. R.U.T.H. dispatches the exact `sfl-strata-archive-broker` identity. The broker retrieves bounded snapshots and passages; only the Author has document-writing tools. Thematic specialists and judges are tool-free. All models inherit the active session model/provider.

Example: “Compare the meaning of systems in the declared 2016–2019 notes with this current essay. Quote both contexts, distinguish vocabulary changes from changed commitments, and propose useful fragments without altering the originals.”

## Tools and boundaries

The archive server supplies archive_status, list_archive_directory, inventory_archive, read_note, host_snapshot, git_history, map_archive, term_timeline and compare_vectors. No separate filesystem MCP server or wildcard tool additions are required. Simple directory requests use a bounded nonrecursive metadata listing, not a full analysis pipeline. A binding failure requires a blocked result rather than repeated speculative calls.

Collection is bounded by explicit roots, exclusions, file/directory/byte caps and UTF-8 note formats. It skips symlinks, hidden paths and credential-like names. Host snapshots are current load/uptime/process-name observations, not behavioral history. No keystrokes, browser history, command arguments, screenshots, background monitor or remote embedding service is installed. Reads can still affect filesystem access-time metadata.

Declared dates and file mtime are different evidence; neither proves when an idea began. Git history records commit/author dates, not historical content. Maps separate explicit links, excerpt TF-IDF candidates and supplied embedding cosine. This is not a graphify adapter or embedding generator. Similarity does not establish equivalence, causal influence or personal development.

R.U.T.H. obtains actual packet hashes using prepare_blind, runs three new blind judge sessions, retrieves targeted evidence, calls prepare_cross, and runs cross-examination against one shared source revision. check_final verifies packet consistency, three current judgments and five gates before acceptance; two repair rounds maximum. These are consistency tools, not a scheduler or truth detector. Fresh sessions and stop-on-error are orchestration instructions, not hard host enforcement.

Original notes remain unchanged by collectors. Source changes and aliases are proposals; document outputs belong outside archive roots. Author output scope remains model policy, not an OS sandbox. R.U.T.H. and the broker inherit MCP, which may expose other configured services; routing only through bundled tools is policy. Local collection does not make the configured LLM local.

## Diagnose the native installation

Run the optional diagnostic against the actual installed directory:

```bash
python3 scripts/diagnose.py --plugin-dir /path/to/installed/sfl-strata --probe --native
```

Use `--config` for an explicitly overridden settings file. Direct probes call only status/discovery. The documented default managed plugin location is `~/.gemini/config/plugins/sfl-strata`; use your actual installation if different.

## Verification

```bash
agy plugin validate --strict /path/to/extracted/sfl-strata
python3 sfl-strata/scripts/check_native_packaging.py
python3 sfl-strata/scripts/check_wizard.py
python3 sfl-strata/scripts/check_plugin.py
python3 sfl-strata/scripts/check_review_packets.py
python3 sfl-strata/scripts/check_review_mcp.py
```

Recorded validation covers native strict validation on Antigravity CLI 1.5.3, headless wizard navigation at 80×24 and larger, fixture-based source collection/review checks, real stdio MCP calls and policy reload in an already-running worker. No global native installation, authenticated model execution or user archive scan was performed during this build. Live tool binding and role behavior still need target-machine verification.
