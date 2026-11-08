---
name: sfl-technical-writing
description: "Use when creating, drafting, revising, or auditing technical documentation (READMEs, system overviews, feature descriptions, architecture docs, KB articles, postmortems) using Systemic Functional Linguistics (SFL) at Target Intensity 9/10: congruent Field construal, K1-by-evidence Tenor calibration, New->Given quantitative Mode cohesion, genre templates, and the 5-point validation gate."
user-invocable: true
---

# SFL Technical Writing (Target Intensity: 9/10)

Create, audit, and edit technical documentation using formal Systemic Functional Linguistics.

## Core Resources
- `references/process-type-validation.md` — Material, Relational, and Cognitive-Mental process checkers.
- `references/modality-calibration.md` — K1-by-evidence rules, Escape Hatches, and SFL editing operations.
- `templates/` — `system-overview.md`, `feature-description.md`, `kb-article-rewrite.md`.

## Step 1 — Set the Register
Fix the three register variables before drafting or auditing:
- **Field (Ideational):** Concrete system entities, Material transformations, Relational dependencies, and densified circumstances (time, `path:line`, exact measure) + task type (`create` | `structural-edit` | `audit`).
- **Tenor (Interpersonal):** Primary Knower (K1) claimed strictly by evidence; peer-practitioner authority; rationed cognitive hedges with Escape Hatches; graduated ideational scale and concession-and-reversal engagement.
- **Mode (Textual):** Markdown staged by genre template; HyperTheme section openers; New->Given quantitative cohesive ties; marked circumstantial themes routing the reader; active Register Dial (`Full Voice` periodic prose vs. `Compressed` reference).

## Step 2 — Apply the Three Metafunctions (9/10 Grammar)

### 1. Ideational (Field): Congruent Construal & Process Discipline
Unpack grammatical metaphors (nominalizations) into concrete, referentially stable participants and checkable processes:
- **Material Processes (System Transformations — High Modality):** Specify exact input formats, transformation logic, output parameters, and circumstantial bounds (`path:line`, load limits, latency). Zero personification.
- **Relational Identifying Processes (Architecture & State — High/Medium Modality):** Map structural containment, quantified attributes (`"spans 412 tables"`), functional dependencies, and explicit failure propagation bounds.
- **Mental Processes (Cognitive Scaffolding & Rationed Unknowns — Medium/Low Modality):**
    - *User Decisions (where required by genre):* Map concrete decision thresholds and measured onboarding timeframes (`"2-3 sessions"`), never vague adjectives (`"easy to learn"`).
    - *Speaker Cognition:* Restricted strictly to flagging empirical unknowns (`"I cannot verify..."`) paired with an Escape Hatch. Never use Mental processes for affective feelings or speculation.

### 2. Interpersonal (Tenor): K1 Modality & Negative Capability
- **High (`does`, `is`, `always`, `never`, `completes within`):** Empirically verified, tested, or code-enforced facts ONLY.
- **Medium (`typically`, `usually`, `most`):** Reproducible observed patterns.
- **Low (`may`, `might`, `I note`, `I suspect`):** Rationed to unverified mechanics; must state the **Escape Hatch** (what test/source promotes it to High).
- **Concession-and-Reversal:** Frame counter-intuitive scale or breaking changes via documented reversal (`"— which sounds improbable, but is benchmarked at..."`).
- **Negative Capability:** State what the system does **not** do and its failure bounds without euphemism.

### 3. Textual (Mode): HyperTheme & Quantitative Cohesion
- **Macro-Order:** Concrete, measured facts precede conditional projections.
- **Theme-Rheme Chains:** Open sections with a HyperTheme; link each paragraph's Theme to the prior paragraph's New.
- **Quantitative Cohesive Ties:** A specific metric or count introduced as **New** returns in the subsequent clause/paragraph as **Given** Theme.
- **Circumstantial Routing:** Use marked themes of time, version, and location (`At ingest.py:208...`) to move the reader structurally through the system.

## Step 3 — Select Genre Template
Load from `templates/`: `system-overview.md`, `feature-description.md`, or `kb-article-rewrite.md` (or adapt staging for postmortems/APIs while preserving process-type mapping and Negative Capability sections).

## Step 4 — Execution Workflows
- **Create Workflow:** Set Register -> Gather concrete participants/quantities/paths -> Draft via template with explicit process-type mapping and New->Given ties -> Run Step 5 Validation Gate.
- **Edit Workflow:** Set Register -> Annotate clauses (`process type | congruent vs. nominalized | K1 modality | Theme/New tie`) -> Emit findings as `claim (quote) -> problem class -> evidence needed -> rewrite` -> Apply surgical edits -> Run Step 5 Validation Gate.

## Step 5 — Linguistic Validation Gate (Mandatory)
1. **Congruent Process Coverage:** All nominalizations unpacked; Material claims carry input, transformation, output, and checkable circumstance (`path:line` + measure).
2. **K1 Modality & Escape Hatch Audit:** Zero unbacked absolutes; zero hedged verifiable facts; every Low-modality claim carries an Escape Hatch; zero affective emotional commentary.
3. **HyperTheme & New->Given Progression:** Concrete precedes conditional; zero orphaned Themes; specific quantities chain across clauses as New->Given ties.
4. **Connective & Circumstantial Integrity:** Every causal/temporal/adversative connective reflects a real code or dataflow edge; circumstantial themes route rather than decorate.
5. **Negative Capability:** System non-capabilities and failure bounds are stated plainly without euphemism.