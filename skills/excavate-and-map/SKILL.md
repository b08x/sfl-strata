---
name: excavate-and-map
description: Use R.U.T.H. and archaeology/cartography teams to retrieve scoped workstation archive evidence, compare concepts over time, and produce independently reviewed present-day synthesis.
---

# Excavate, map, and recontextualize

## Exact delegation roster

- archive-broker: `sfl-strata-archive-broker`
- author: `sfl-strata-author`
- concept-drift-analyst: `sfl-strata-concept-drift-analyst`
- docs-ideational-judge: `sfl-strata-docs-ideational-judge`
- docs-interpersonal-judge: `sfl-strata-docs-interpersonal-judge`
- docs-textual-judge: `sfl-strata-docs-textual-judge`
- friction-analyst: `sfl-strata-friction-analyst`
- regeneration-curator: `sfl-strata-regeneration-curator`
- semantic-cartographer: `sfl-strata-semantic-cartographer`
- stratigraphic-chronologist: `sfl-strata-stratigraphic-chronologist`
- vector-bridge-interpreter: `sfl-strata-vector-bridge-interpreter`

## Binding preflight and failure handling (0.1.1)

For a directory-listing request, perform only a scoped listing, not the full research/review pipeline. The plugin supplies its own archive MCP server. It does NOT require a generic filesystem server, filesystem wildcards in agent tools, or blanket Always Allow permissions. Built-in tool availability, MCP server tool enablement, approval rules, and archive root scope are distinct layers.

First inspect the live injected agent roster and eager tool schemas. Select this plugin's exact runtime server/tool identities from those schemas; do not synthesize names from punctuation conventions. The expected package-local servers are archive and review_packets, normally plugin-prefixed by the loader. Use archive_status to confirm the actual version and configured roots without collecting data. If it reports no roots, report the configuration gap; do not treat it as denied filesystem access. A request to list a directory maps to list_archive_directory with a confirmed root_index and relative_path, not read_note('.') or a guessed filesystem tool. If directory meaning is unclear and cannot be resolved from configured roots, request the missing path without making tool calls against guessed locations.

Delegate retrieval to the EXACT discovered identity corresponding to sfl-strata-archive-broker. The role label archive-broker is not the agent identifier. Human display names and persona labels are not callable identities. Never strip sfl-strata-, invent an alias, or repeatedly invoke a missing child. If the runtime roster qualifies names, use its exact qualified identity only after confirming it matches the declared profile. Missing child discovery means BLOCKED with the expected identity and observed error.

When any tool call returns 'not enabled', 'not allowed', an unknown server/tool/agent, or a binding/permission conversion failure: STOP that branch. Do not repeat the failed call, try punctuation variants, call wildcards, substitute another filesystem server, restart the session, or recommend broadening permissions. Resume only after an actual configuration/runtime change has been verified; user intent to grant permission is not evidence that binding succeeded. Return the exact failed identity, argument shape (without secrets), error and failing layer if known. Mark unknown layers unknown. Do not claim a root cause from the error alone. Do not invent config keys such as allowed_tools, claim a misspelled path, or prescribe a filesystem:* policy without installed-version evidence.

A wildcard is never a callable tool name. Model explanations of tool errors are hypotheses, not configuration evidence. If the plugin's archive tools are absent, report that bootstrap failed and point to the packaged diagnose.py; do not improvise MCP setup or external package installation. All previous no-mutation and evidence constraints remain in force. This protocol is a model instruction; it does not guarantee the model will stop unless the host enforces it.


R.U.T.H. (Records Uncertainty, Traces History) owns the brief, captured scope, provenance ledger, revisions, review handoffs and final delivery. This is a workstation variant of sfl-writer, not an assertion that all old material describes a coherent personal evolution.

1. Scope: select a present question or essay and explicitly configured archive roots, date interval, exclusions, output paths outside roots, and desired deliverables. Use the configured one-shot tools; no daemon, schedule, keystroke logging, browser history, or screen capture is installed. Tool server startup does not scan. If roots/content/host permissions are absent, report that limit. Do not change them automatically.
2. Retrieve: dispatch sfl-strata-archive-broker to inventory the archive and supply exact passages and dates. Use host_snapshot only when enabled and relevant to the question. A current process-name count suggests where to investigate; it does not prove attention, interests over ten years, or abandoned work. Use Git history only when enabled. Preserve differences between declared note dates, mtime, version metadata, and known historical events. The source snapshot hash is the repository_revision for this workflow.
3. Analyze: dispatch the three archaeology roles and three cartography roles with the SAME source snapshot and present brief. They are independent leaf advisors, not tools or autonomous collectors. Require original source quotes, alternate interpretations, counter-evidence and usefulness judgments labeled as proposals. Run only roles relevant to the task, but name any skipped role. The full-team option runs all six.
4. Draft: the Author writes an adapted genre (concept-drift report, archival atlas, regeneration dossier, or present-day essay). Use the bundled templates under this skill. Distinguish explicit links, lexical matches, embedding similarity, temporal proximity, hypothesis and quoted-source support. Chronological succession alone does not establish influence. Reframe abandoned as inactive within captured evidence unless abandonment is explicitly documented.
5. Blind audit: call review_packets.prepare_blind with the candidate and register/template to obtain its actual hash. Open THREE FRESH judge sessions. Each gets only that inline draft/register/identity packet; existing draft citations remain. No peer findings or standalone evidence packet. Judges are tool-free. Blind verdicts are PROVISIONAL or BLOCKED, never PASS.
6. Cross-examine: broker binds targeted evidence to the same candidate/source snapshot. Call review_packets.prepare_cross with the three frozen blind judgments and evidence. It computes the evidence digest and rejects identity errors. Send the SAME shared packet to fresh sessions of all three judges; they now receive peer findings and evidence. Record defended, withdrawn, resolved and deadlocked findings. Proposed rewrites introduce claims that also need evidence.
7. Revise and deliver: return edits to the sole Author. Any substantive change increments document_revision and requires a new blind/cross cycle. At most two repair rounds. Call review_packets.check_final on three current cross judgments and the five gates before acceptance. An accepted packet is a consistency result, not proof of historical interpretation. Unsupported asserted claims, unresolved blockers and provisional Scout evidence cannot pass. NOT_APPLICABLE needs a scope-based reason. Deliver PARTIAL/BLOCKED when limits remain; do not invent stronger evidence to finish.

Only the Author writes deliverables; collector tools do not alter source files. Proposals for graph/filename/alias changes stay unapplied. Store ledgers, reports and review records only in the authorized output scope. No claim of cross-session memory without an actual save. Preserve source IDs, content hashes, collection policy, snapshot, exclusions, date provenance, quoted passages, edge method/model/threshold, current brief, uncertainties and decisions. A scope or source change invalidates affected evidence.

Invoke the exact declared child names using the live Antigravity tool schemas. Children do not inherit your conversation. Do not substitute generic self or unrestricted agents. R.U.T.H. and the broker inherit MCP to reach the local servers; this can also expose configured third-party MCP tools. Use only the plugin's archive/review operations for this workflow, and never claim enforced broker-only transport isolation. No remote collection or embedding provider is bundled. Inherited model/provider settings still govern LLM processing of supplied note text; local collection does not make the LLM local.

Host and collector limits are real implementation boundaries; the Author's output-path separation and role conduct are model instructions, not an OS sandbox. The packet helper validates actual calls, but does not schedule judges, prove fresh-session blindness, or establish empirical truth. Native Antigravity behavior requires target-machine validation.
