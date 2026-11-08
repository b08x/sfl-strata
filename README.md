# SFL Strata — Antigravity field notebook

**Version 0.3.0.** SFL Strata is an archive-analysis plugin for the Antigravity CLI: it indexes explicitly selected note directories and runs multi-agent, reviewed recontextualization over them. It is built for people with existing personal archives who want to revisit them — and the "field notebook" name is literal about method: the plugin treats a note archive as archaeological strata, layered and dated and reinterpretable, where each evidence type (file mtime, git history, declared dates, drifting vocabulary) is a separate layer. The tools read those layers as layers, never flattening them into one timeline; maps and timelines chart emergent drift across the layers, they do not extract a hidden truth. **R.U.T.H.** — the `sfl-strata-coordinator` profile — coordinates archaeology, stratigraphy and semantic cartography across explicitly selected archive directories. What the plugin reads is bounded: explicit roots, and only through bundled, bounded tools. The full boundary list is up front in [What it can and cannot read](#what-it-can-and-cannot-read).

## What it can and cannot read

Every collection and tool call is bounded:

- Collection is bounded by explicit roots, exclusions, file/directory/byte caps and UTF-8 note formats.
- It skips symlinks, hidden paths and credential-like names.
- Simple directory requests use a bounded nonrecursive metadata listing, not a full analysis pipeline.
- Host snapshots are current load/uptime/process-name observations, not behavioral history.
- Reads can still affect filesystem access-time metadata.

What it never does:

- No archive inventory, note contents or host observation is requested by setup.
- No keystrokes, browser history, command arguments, screenshots, background monitor or remote embedding service is installed.
- Source notes are never edited by setup or collection.
- Status sockets expose no collection operations and run only for the MCP process lifetime.

The full mechanism detail stays in [Tools and boundaries](#tools-and-boundaries).

## Prerequisites

- **Python 3 with venv/pip and internet access on first run.** Setup prepares an isolated Python environment under `$XDG_DATA_HOME/sfl-strata/runtime` (normally `~/.local/share/sfl-strata/runtime`) if its dependencies are unavailable. It installs Textual 8.2.8, jsonschema 4.x and PyYAML 6.x there. It does not alter system Python.
- **Offline machine:** provision Textual 8.2.8, jsonschema 4.x and PyYAML 6.x in advance; the bootstrap is not an offline dependency bundle. MCP startup never downloads packages.
- **Antigravity CLI** (`agy`). Recorded validation used Antigravity CLI 1.5.3.

## Start here

Setup runs as a keyboard-driven Textual wizard: `configure.py` opens it automatically when no config arguments are given. Extract the archive and launch setup from the extracted directory:

```bash
cd sfl-strata
python3 configure.py
```

The wizard's five pages, one decision each:

- **Orientation** — introduction to the setup.
- **Archive roots** — the archive folder browser together with the list of explicit roots.
- **Capabilities** — the separate note-text, Git-history and current-host switches.
- **Boundaries** — the collection budgets.
- **Review & connect** — the policy review and connection verification.

Keyboard and display: use Tab/Shift+Tab and Enter/Space, Ctrl+N to continue, Ctrl+P to go back, and Ctrl+Q to exit. Escape cancels the folder picker. Layouts support 80×24 and larger terminals; pages scroll when needed. True-color terminals show the archival-paper, rust and olive palette; NO_COLOR is respected. Draft settings are written only when you choose **Save & verify**.

**Save & verify** closes the configurer's own loop: it checks what was just written and asks already-running workers what they actually loaded. It checks the saved revision and calls status through a fresh stdio MCP process; it separately queries private, status-only local Unix sockets belonging to already-running 0.2 workers, and matching revisions establish that those observed workers loaded the policy. If local sockets are unavailable, live status is shown as unobserved. Status sockets expose no collection operations and run only for the MCP process lifetime. **“Live session not observed” is explicitly unverified; a fresh-process success does not establish that the active Antigravity agent has tools bound.**

After verification, choose **Install plugin** to hand the reviewed directory to `agy plugin install`. Antigravity owns installation and any upgrade prompts.

### Direct install (headless)

You can also install directly and engage R.U.T.H.:

```bash
agy plugin install "$PWD"
agy --agent sfl-strata-coordinator
```

The install target is the extracted directory. This is an Antigravity CLI plugin with plugin.json, agents/, skills/ and bundled MCP servers.

### Upgrading or reconfiguring an existing install

- Existing installations can run configure.py in their installed plugin directory too.
- Reinstall the updated package and reconnect once when upgrading older MCP workers.
- Avoid duplicate native and historical project-scoped copies, since they can shadow one another.
- Importing a pre-0.2 policy: the native worker imports an existing `${PLUGIN_DATA}/workstation.json` only when the shared file does not exist; otherwise shipped defaults initialize it with no roots and all optional capabilities disabled. The wizard itself uses existing shared settings or bundled defaults; to import a pre-0.2 policy before first worker startup, configure the old file explicitly or let the updated worker perform its one-time migration first. Arbitrary old installations are not searched.

## Settings and verification

The wizard and archive worker share `$XDG_CONFIG_HOME/sfl-strata/workstation.json`, normally `~/.config/sfl-strata/workstation.json`. Settings live outside the installed package and survive replacement. The file's shape, with example values — the shipped defaults are no roots with all optional capabilities disabled:

```json
{
  "roots": ["/absolute/path/to/vault"],
  "content_enabled": true,
  "git_history_enabled": true,
  "host_usage_enabled": false,
  "max_files": 2000,
  "max_dirs": 10000,
  "max_file_bytes": 262144,
  "max_total_bytes": 33554432,
  "max_excerpt_chars": 1200,
  "extensions": [".md", ".txt", ".org", ".rst", ".adoc"],
  "exclude_names": [".git", ".ssh", ".gnupg", "node_modules", "__pycache__"],
  "exclude_globs": ["*.pem", "*.key", "*credentials*", "*password*"]
}
```

A running 0.2 worker validates and reloads changes before every tool request; changed policy invalidates its cached evidence. Invalid settings block collection instead of retaining old permissions. No routine restart is needed after configuring a 0.2 worker. `archive_status` reports its configuration path, policy revision and live-reload support — the three facts to check after any edit.

Scriptable configuration remains available and preserves unspecified settings:

```bash
python3 configure.py --root /absolute/path/to/vault --text --git-history
python3 configure.py --no-text --max-files 1500
```

Every flag:

- `--config /path/workstation.json` — explicitly overrides the settings file (default `$XDG_CONFIG_HOME/sfl-strata/workstation.json`). A custom file must also be passed to the archive server with `--config`; changing only the wizard path does not retarget an existing worker.
- `--root PATH` — add an explicit root. Repeat `--root` for multiple roots; `--roots` is accepted as an alias.
- `--text` / `--no-text` — note-text capability.
- `--git-history` / `--no-git-history` — Git-history capability.
- `--host-usage` / `--no-host-usage` — current-host usage.
- `--max-files N` — file budget.
- `--wizard` — run the wizard explicitly (it launches automatically when no config arguments are given).

Exclusions and note extensions are shown in the wizard and remain editable in JSON. Source notes are never edited by setup or collection.

## Teams and work

Tool access is tiered by design: each agent level has a distinct tool surface, so analysis, retrieval, writing and judgment never collapse into one agent. R.U.T.H. dispatches the exact `sfl-strata-archive-broker` identity. The broker retrieves bounded snapshots and passages; only the Author has document-writing tools. Thematic specialists and judges are tool-free. All models inherit the active session model/provider.

There are 12 profiles in three teams:

| Team | Roles | Profile IDs |
| --- | --- | --- |
| Archaeology & Stratigraphy | Stratigraphic Chronologist, Concept Drift Analyst, Regeneration Curator | `sfl-strata-stratigraphic-chronologist`, `sfl-strata-concept-drift-analyst`, `sfl-strata-regeneration-curator` |
| Semantic Cartography & Topography | Semantic Cartographer, Vector Bridge Interpreter, Friction Analyst | `sfl-strata-semantic-cartographer`, `sfl-strata-vector-bridge-interpreter`, `sfl-strata-friction-analyst` |
| Evidence and review | Archive Broker, Author, Ideational/Interpersonal/Textual Judges, R.U.T.H. | `sfl-strata-archive-broker`, `sfl-strata-author`, `sfl-strata-docs-ideational-judge`, `sfl-strata-docs-interpersonal-judge`, `sfl-strata-docs-textual-judge`, `sfl-strata-coordinator` |

A working invocation, exercising the layer-separation rules from Tools and boundaries: “Compare the meaning of systems in the declared 2016–2019 notes with this current essay. Quote both contexts, distinguish vocabulary changes from changed commitments, and propose useful fragments without altering the originals.”

## Tools and boundaries

The archive server supplies `archive_status`, `list_archive_directory`, `inventory_archive`, `read_note`, `host_snapshot`, `git_history`, `map_archive`, `term_timeline` and `compare_vectors`. No separate filesystem MCP server or wildcard tool additions are required. Simple directory requests use a bounded nonrecursive metadata listing, not a full analysis pipeline. A binding failure requires a blocked result rather than repeated speculative calls.

Collection is bounded by explicit roots, exclusions, file/directory/byte caps and UTF-8 note formats. It skips symlinks, hidden paths and credential-like names. Host snapshots are current load/uptime/process-name observations, not behavioral history. No keystrokes, browser history, command arguments, screenshots, background monitor or remote embedding service is installed. Reads can still affect filesystem access-time metadata.

### What the evidence layers do and don't prove

Declared dates and file mtime are different evidence; neither proves when an idea began. Git history records commit/author dates, not historical content. Maps separate explicit links, excerpt TF-IDF candidates and supplied embedding cosine. This is not a graphify adapter or embedding generator. Similarity does not establish equivalence, causal influence or personal development.

### What collection does to your notes

- Original notes remain unchanged by collectors.
- Source changes and aliases are proposals; document outputs belong outside archive roots.
- Author output scope remains model policy, not an OS sandbox.
- R.U.T.H. and the broker inherit MCP, which may expose other configured services; routing only through bundled tools is policy.
- Local collection does not make the configured LLM local.

### The R.U.T.H. review pipeline

The review is the plugin's archaeology of itself: its own output sessions get the same layered-evidence discipline, re-read by fresh judges.

1. R.U.T.H. obtains actual packet hashes using `prepare_blind`.
2. Three new blind judge sessions run.
3. Targeted evidence is retrieved.
4. `prepare_cross` is called, and cross-examination runs against one shared source revision.
5. `check_final` verifies packet consistency, three current judgments and five gates before acceptance; two repair rounds maximum.

These are consistency tools, not a scheduler or truth detector. Fresh sessions and stop-on-error are orchestration instructions, not hard host enforcement.

## Diagnose the native installation

This closes the loop between the installed artifacts and the configured runtime — the diagnostic reads the actual installation, not the docs. Run the optional diagnostic against the actual installed directory:

```bash
python3 scripts/diagnose.py --plugin-dir /path/to/installed/sfl-strata --probe --native
```

Use `--config` for an explicitly overridden settings file. Direct probes call only status/discovery. The documented default managed plugin location is `~/.gemini/config/plugins/sfl-strata`; use your actual installation if different.

## Verification

These commands close the third self-inspection loop — package, wizard, servers and review machinery checked without touching your notes.

```bash
agy plugin validate --strict /path/to/extracted/sfl-strata  # strict manifest validation
python3 sfl-strata/scripts/check_native_packaging.py        # packaging/asset consistency
python3 sfl-strata/scripts/check_wizard.py                 # wizard navigation (headless)
python3 sfl-strata/scripts/check_plugin.py                # plugin manifest and assets
python3 sfl-strata/scripts/check_review_packets.py         # review packet fixtures
python3 sfl-strata/scripts/check_review_mcp.py            # review MCP stdio calls
python3 sfl-strata/scripts/check_bootstrap.py             # bootstrap environment
```

**Live tool binding and role behavior still need target-machine verification.**

Recorded validation covers:

- native strict validation on Antigravity CLI 1.5.3,
- headless wizard navigation at 80×24 and larger,
- fixture-based source collection/review checks,
- real stdio MCP calls and policy reload in an already-running worker.

Caveats:

- No global native installation, authenticated model execution or user archive scan was performed during this build.
- Live tool binding and role behavior still need target-machine verification.

## Conclusion

Before pointing SFL Strata at a real archive, run the check scripts against the extracted directory and `scripts/diagnose.py` against the installed one, and confirm **Save & verify** reports a live running worker. What you reviewed on the wizard's Boundaries page is what the workers enforce. Verify the live tool binding on your machine, then hand over your strata.
