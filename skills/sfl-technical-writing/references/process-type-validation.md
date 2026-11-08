# Process Type Validation — Ideational Checkers (Target Intensity: 9/10)

Run every technical claim through the matching checker below. Enforce **Congruent Construal**: participants must be concrete, individually identifiable, and referentially stable (proper-named modules, exact function signatures, bounded file paths, dated commits). Unpack all grammatical metaphors (nominalizations) into active verbs.

---

## 1. Material Process Checker (System Transformations — High Modality)
For every system capability or execution claim, verify all four components:
- **Concrete Input Participants:** Exact data structures, payload schemas, or signals entering the process.
  - *Fail (Vague):* "processes user data"
  - *Pass (Congruent):* "`IngestWorker` (`worker.go:42`) parses 64KB JSON user profile payloads..."
- **Explicit Transformation Logic:** The exact algorithm, state mutation, or syscall executed.
  - *Fail (Nominalized):* "performs content analysis via model inference"
  - *Pass (Congruent):* "...classifies token sequences using an ONNX-quantized RoBERTa model (`model.onnx`)..."
- **Concrete Output Participants:** Exact return types, mutated rows, or emitted events with measured parameters.
  - *Fail (Vague):* "provides actionable insights"
  - *Pass (Congruent):* "...and writes normalized `user_record` rows to PostgreSQL (`schema.sql:108`) with a 95% confidence threshold."
- **Densified Circumstances (Verification Conditions):** Exact file paths (`path:line`), execution bounds, concurrency limits, or latencies.
  - *Fail (Uncheckable):* "works reliably under load"
  - *Pass (Checkable):* "Completes within 14ms at p99 under 1,000 RPS (`bench_test.go:88`)."

---

## 2. Relational Identifying & Attributing Checker (Architecture & State — High/Medium Modality)
For structural, containment, and dependency claims, verify:
- **Quantified Structural Containment:** Exact component counts, sizes, and topological boundaries.
  - *Fail (Vague):* "features a modular microservice architecture"
  - *Pass (Quantified):* "The `api-gateway` binary (`main.rs:19`) embeds 3 middleware stages and routes traffic across 4 downstream gRPC services."
- **Explicit Functional Dependencies & Failure Propagation:** Exact upstream requirements and bounded fallback mechanics.
  - *Fail (Nominalized):* "integrated payment system with high availability"
  - *Pass (Congruent):* "`ChargeService` requires an active `auth-token` lease and PostgreSQL write quorum; when quorum drops, `ChargeService` reads cached permissions from Redis (`cache.go:211`) for exactly 600 seconds before rejecting requests with HTTP 503."

---

## 3. Mental Process Checker (Rationed Cognition & Decision Thresholds — Medium/Low Modality)
Mental processes are strictly restricted to two valid contexts. Never use Mental processes for affective emotion ("I find comfort") or unbacked speculation about code internals.
- **Context A — Rationed Speaker Uncertainty (Low Modality):** Used ONLY when flagging an unverified empirical gap. Must use first-person cognitive verbs (`I note`, `I suspect`, `I cannot verify`) paired with an **Escape Hatch**.
  - *Pass:* "I cannot verify whether `prune_wal()` blocks concurrent readers under lock contention; running `go test -race ./storage/...` against line 144 will confirm."
- **Context B — Quantified User Decision Scaffolding (Medium Modality, User-Facing Guides Only):** Used only when a genre template requires mapping operator/user onboarding or decision points. Must specify measurable timeframes or session counts.
  - *Fail (Vague):* "users easily understand the dashboard"
  - *Pass (Quantified):* "Operators typically isolate p99 latency spikes within 2 to 3 triage sessions using the flamegraph view (`ui/flame.tsx:90`)."

---

## Participant-Circumstance Matrix

| Process Type   | Primary Participants                               | Required Circumstances                         | Verification Source                            |
|:---------------|:---------------------------------------------------|:-----------------------------------------------|:-----------------------------------------------|
| **Material**   | Input Struct -> Module/Function -> Output State    | `path:line`, latency, byte size, load bound    | Source code, benchmarks, test suites           |
| **Relational** | Component A <-> Component B (Quantified)           | Containment hierarchy, timeout/fallback bounds | AST call graphs, config files, schemas         |
| **Mental**     | Speaker -> Empirical Gap (or Operator -> Decision) | Escape Hatch check (or measured session count) | Audit gap log (or reproducible user telemetry) |