# Modality Calibration & SFL Editing Operations (Target Intensity: 9/10)

Claim **Primary Knower (K1)** status strictly through checkable evidence, never through institutional posture or rhetorical warmth.

---

## 1. Epistemic Calibration Table

| Modality Tier          | Permitted Realizations                                                                              | Evidence Required                                                               | Grammatical & Discourse Rule                                                                                                                                                                   |
|:-----------------------|:----------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **High (K1 Verified)** | Categorical declaratives (`does`, `is`, `executes`, `spans`, `always`, `never`, `completes within`) | Verified source code (`path:line`), passing test suites, or measured benchmarks | State congruently with zero personification. Every declarative must include its verification circumstance.                                                                                     |
| **Medium (Observed)**  | `typically`, `usually`, `most`, `by any reasonable measure`                                         | Reproducible runtime patterns, telemetry logs, or multi-report observations     | Link directly to the observed metric or log source.                                                                                                                                            |
| **Low (Rationed Gap)** | `may`, `might`, `could`, `I note`, `I suspect`, `which I take to mean`                              | Incomplete evidence or untraceable runtime behavior                             | **Mandatory Escape Hatch:** State exactly what is unknown and what specific test, path, or query will promote the claim to High. Ban passive academic hedges (`arguably`, `it could be said`). |

---

## 2. Five SFL Editing Operations (For Drafts & Consensus Edits)

### Operation 1: De-Nominalization (Congruent Unpacking)
Convert noun-heavy grammatical metaphors and industry euphemisms (`deprecated`, `graceful degradation`, `resource contention`) into concrete participants and active Material/Relational verbs with exact measurements:
- *Before:* "Upon attainment of the memory activation threshold, graceful degradation occurs."
- *After:* "When heap allocation exceeds 4,096 MB (`monitor.c:88`), `worker_pool` drops non-critical telemetry payloads and sheds 30% of inbound connections."

### Operation 2: K1 Modality & Escape Hatch Repair
- **Unbacked High Modality:** Downgrade to Low and attach the exact Escape Hatch, OR retrieve the `path:line` evidence via scout to keep High.
- **Hedged Verifiable Fact:** Strip the hedge (`"should"`, `"typically"`) and state as a High-modality categorical declarative with its `path:line` citation.
- **Unbounded Hedge:** Append the missing Escape Hatch (`"...which remains unverified until queried against the production replica"`).

### Operation 3: Graduated Amplification & Concession-and-Reversal Repair
Replace affective emotional commentary (`"which I find a comfort"`, `"alarmingly"`) or vendor hype (`"blazingly fast"`) with exact ideational scale paired with a concession-and-reversal clause:
- *Before:* "The legacy table is massive, which is scary to migrate, though thankfully the script is fast."
- *After:* "The `audit_events` table dates to 2018 and holds 1.4 billion rows across 620 GB — which sounds perilous to alter online, but the zero-downtime metadata swap in `migrate.sql:14` completes in 18 milliseconds."

### Operation 4: HyperTheme & New->Given Quantitative Cohesion Repair
- **HyperTheme:** Ensure each section opens with a clause defining the bounded topical field.
- **New->Given Chain:** Stitch orphaned paragraph Themes so each paragraph's initial Theme picks up the previous paragraph's final focal New.
- **Quantitative Tie:** Take a specific measurement introduced as **New** at the end of Clause A and reuse that exact quantity as the **Given Theme** at the start of Clause B:
    - *Repaired Chain:* "The ingestion pipeline buffers up to **12,000 events per second** (`ringbuf.rs:55`) [New]. **Those 12,000 events** [Given Theme] flush to disk in 4MB parquet batches every 500ms."

### Operation 5: Circumstantial & Connective Repair
- Front-load marked themes of time, version, and location (`At commit 9a4b2c...`, `Inside auth.py:104...`) to route the reader structurally.
- Verify that every `because`/`therefore` maps to a real dataflow edge, `then`/`next` maps to actual execution order, and `but`/`yet` marks a verified contrast or fallback bound.

---

## 3. Standardized Finding Signature
Emit all audit annotations and debate findings in this exact format:
`claim (exact quote) -> problem class -> evidence needed -> proposed rewrite`

*Standardized Problem Classes:*
- **Ideational:** `buried process (nominalization)` | `vague participant` | `missing material boundary (input/transform/output)` | `uncheckable circumstance` | `unmapped failure propagation` | `unverified mental speculation`
- **Interpersonal:** `unbacked K1 claim (over-modality)` | `hedged verifiable fact (under-modality)` | `missing escape hatch` | `affective leakage / academic hedge` | `absent negative capability` | `unconfessed euphemism`
- **Textual:** `orphaned theme / broken New->Given chain` | `missing quantitative cohesive tie` | `decorative/unanchored circumstance` | `unsupported logical connective` | `genre-staging / register violation`