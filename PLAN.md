# Group Dynamics Simulator — Implementation Plan

**Last updated**: 2026-04-24
**Current phase**: Phase 1 — Spreadsheet Prototype
**Design reference**: `Goup Dynamics Simulator - High-Level System Design.md`

---

## Phase Overview

| Phase | Description | Status | Branch |
|-------|-------------|--------|--------|
| 1 | Spreadsheet Prototype | 🟡 In Progress | `claude/plan-group-simulator-5kmcc` |
| 2 | Web Application | ⬜ Not Started | TBD |
| 3 | Transcript & Notes Ingestion | ⬜ Not Started | TBD |
| 4 | Intervention Lab | ⬜ Not Started | TBD |
| 5 | Research Workspace | ⬜ Not Started | TBD |

---

## Phase 1 — Spreadsheet Prototype

**Goal**: Build a working Excel/Google Sheets workbook that:
- Accepts structured psychological assessment inputs per person
- Accepts relationship matrix data
- Computes normalized profile summaries
- Generates a structured AI prompt block ready to paste into Claude
- Provides a paste-back log for simulation outputs
- Includes basic visualizations (heat maps, relationship graph concept)

**Success criteria**: Run at least one complete end-to-end simulation using the spreadsheet — entering real or test data, generating a prompt, running it in Claude, and producing a coherent report. Iterate on the prompt design until outputs are consistently well-formed and evidence-anchored.

### Phase 1 Prototype Contract

This subsection defines the **frozen Phase 1 contract artifacts**. These artifacts are locked interfaces for the spreadsheet prototype and must not change without an explicit contract revision entry in this file.

#### 1) Frozen Artifact: Field Dictionary

Every field uses a stable ID so it can map directly to Phase 2 database columns and API payloads.

| Stable ID | Tab | Type | Allowed values | Validation rule |
|-----------|-----|------|----------------|-----------------|
| `person.id` | People | string | slug/UUID-like identifier | Required; unique across People tab; regex `^[a-z0-9._-]{3,64}$` |
| `person.display_name` | People | string | free text | Required; 1–120 chars |
| `person.role` | People | enum | `leader`, `manager`, `ic`, `advisor`, `observer`, `other` | Required |
| `person.group_membership` | People | string | free text | Required; 1–120 chars |
| `person.authority_level` | People | integer | `1..5` | Required; integer only |
| `person.is_active` | People | boolean | `true`, `false` | Required |
| `person.ocean.openness` | Big Five | integer | `0..100` | Required if person active; integer only |
| `person.ocean.conscientiousness` | Big Five | integer | `0..100` | Required if person active; integer only |
| `person.ocean.extraversion` | Big Five | integer | `0..100` | Required if person active; integer only |
| `person.ocean.agreeableness` | Big Five | integer | `0..100` | Required if person active; integer only |
| `person.ocean.neuroticism` | Big Five | integer | `0..100` | Required if person active; integer only |
| `person.conflict.competing` | Conflict Style | integer | `0..100` | Required; person’s five conflict values must sum to `100 ± 1` |
| `person.conflict.collaborating` | Conflict Style | integer | `0..100` | Required; person’s five conflict values must sum to `100 ± 1` |
| `person.conflict.compromising` | Conflict Style | integer | `0..100` | Required; person’s five conflict values must sum to `100 ± 1` |
| `person.conflict.avoiding` | Conflict Style | integer | `0..100` | Required; person’s five conflict values must sum to `100 ± 1` |
| `person.conflict.accommodating` | Conflict Style | integer | `0..100` | Required; person’s five conflict values must sum to `100 ± 1` |
| `person.psych_safety.item_1` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.psych_safety.item_2` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.psych_safety.item_3` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.psych_safety.item_4` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.psych_safety.item_5` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.psych_safety.item_6` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.psych_safety.item_7` | Psychological Safety | integer | `1..5` | Required for surveyed person |
| `person.comm.directness` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.comm.context_orientation` | Communication & Decision | integer | `0..100` | `0=low-context`, `100=high-context`; bounded integer |
| `person.comm.verbal_dominance` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.comm.listening_quality` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.comm.feedback_tolerance` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.decision.analytical_vs_intuitive` | Communication & Decision | integer | `0..100` | `0=intuitive`, `100=analytical`; bounded integer |
| `person.decision.risk_appetite` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.decision.speed` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.decision.ambiguity_tolerance` | Communication & Decision | integer | `0..100` | Optional but bounded integer |
| `person.eq.perceiving` | Emotional Intelligence | integer | `0..100` | Optional but bounded integer |
| `person.eq.using` | Emotional Intelligence | integer | `0..100` | Optional but bounded integer |
| `person.eq.understanding` | Emotional Intelligence | integer | `0..100` | Optional but bounded integer |
| `person.eq.managing` | Emotional Intelligence | integer | `0..100` | Optional but bounded integer |
| `person.attachment.secure` | Attachment Tendencies | integer | `0..100` | Optional; secure+anxious+avoidant+fearful should sum to `100 ± 1` when all present |
| `person.attachment.anxious` | Attachment Tendencies | integer | `0..100` | Optional; secure+anxious+avoidant+fearful should sum to `100 ± 1` when all present |
| `person.attachment.avoidant` | Attachment Tendencies | integer | `0..100` | Optional; secure+anxious+avoidant+fearful should sum to `100 ± 1` when all present |
| `person.attachment.fearful` | Attachment Tendencies | integer | `0..100` | Optional; secure+anxious+avoidant+fearful should sum to `100 ± 1` when all present |
| `rel.from_person_id` | Relationship Matrix | string | must exist in `person.id` | Required |
| `rel.to_person_id` | Relationship Matrix | string | must exist in `person.id` | Required; cannot equal `rel.from_person_id` |
| `rel.trust` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.influence` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.emotional_closeness` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.respect` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.conflict_intensity` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.dependency` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.communication_frequency` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.avoidance` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.alliance` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.power_differential` | Relationship Matrix | integer | `0..100` | Optional but bounded integer |
| `rel.evidence_source` | Relationship Matrix | enum | `validated`, `self_report`, `observed`, `inferred`, `missing` | Required per pair |
| `rel.notes` | Relationship Matrix | string | free text | Optional; max 500 chars |
| `group.id` | Group Context | string | slug/UUID-like identifier | Required; unique |
| `group.type` | Group Context | enum | `team`, `leadership_team`, `project_team`, `board`, `other` | Required |
| `group.structure` | Group Context | enum | `formal`, `informal`, `hybrid` | Required |
| `group.shared_goals` | Group Context | string | free text | Required; 1–1000 chars |
| `group.norms.explicit` | Group Context | string | free text | Optional |
| `group.norms.implicit` | Group Context | string | free text | Optional |
| `group.psychological_safety_aggregate` | Group Context | integer | `0..100` | Computed; read-only |
| `group.decision_rules` | Group Context | string | free text | Optional |
| `group.conflict_history` | Group Context | string | free text | Optional |
| `group.stress_level` | Group Context | integer | `1..5` | Required |
| `group.role_clarity` | Group Context | integer | `0..100` | Optional but bounded integer |
| `group.cultural_context` | Group Context | string | free text | Optional |
| `group.environmental_constraints` | Group Context | string | free text | Optional |
| `scenario.id` | Scenario Builder | string | slug/UUID-like identifier | Required; unique |
| `scenario.title` | Scenario Builder | string | free text | Required; 1–200 chars |
| `scenario.type` | Scenario Builder | enum | `conflict`, `decision`, `change`, `crisis`, `performance`, `other` | Required |
| `scenario.trigger_event` | Scenario Builder | string | free text | Required; 1–2000 chars |
| `scenario.stakes_level` | Scenario Builder | integer | `1..5` | Required |
| `scenario.emotional_intensity` | Scenario Builder | integer | `1..5` | Required |
| `scenario.ambiguity_level` | Scenario Builder | integer | `1..5` | Required |
| `scenario.time_pressure` | Scenario Builder | integer | `1..5` | Required |
| `scenario.resource_constraints` | Scenario Builder | string | free text | Optional |
| `scenario.public_visibility` | Scenario Builder | boolean | `true`, `false` | Required |
| `scenario.required_decision` | Scenario Builder | string | free text | Required |
| `scenario.success_criteria` | Scenario Builder | string | free text | Required |
| `scenario.failure_consequences` | Scenario Builder | string | free text | Required |
| `scenario.known_facts` | Scenario Builder | list[string] | newline-delimited text list | Optional |
| `scenario.uncertain_facts` | Scenario Builder | list[string] | newline-delimited text list | Optional |
| `scenario.intervention_options` | Scenario Builder | list[string] | newline-delimited text list | Optional |
| `sim.run_id` | Simulation Config / Log | string | timestamp + suffix | Required; unique |
| `sim.passes` | Simulation Config | integer | `1..10` | Required |
| `sim.randomness` | Simulation Config | enum | `low`, `medium`, `high` | Required |
| `sim.depth` | Simulation Config | enum | `surface`, `standard`, `deep` | Required |
| `sim.dialogue_enabled` | Simulation Config | boolean | `true`, `false` | Required |
| `sim.report_detail_level` | Simulation Config | enum | `summary`, `standard`, `full` | Required |
| `sim.intervention_mode` | Simulation Config | enum | `baseline`, `compare` | Required |
| `sim.evidence_strictness` | Simulation Config | enum | `strict`, `moderate`, `lenient` | Required |
| `sim.guardrail_verbosity` | Simulation Config | enum | `minimal`, `standard`, `verbose` | Required |

#### 2) Frozen Artifact: Scoring Spec

- **Normalization formula (default bounded scale)**:  
  `normalized_0_100 = ROUND(100 * (raw - raw_min) / (raw_max - raw_min), 0)`  
  with clamp: `MIN(100, MAX(0, normalized_0_100))`.
- **Reverse-key formula** (if source instrument has reverse-coded item):  
  `raw_reversed = raw_max + raw_min - raw`.
- **Big Five domain score**: average of keyed item raws for the trait, then apply normalization formula to trait raw range.
- **Psychological safety per-person score**: mean of 7 items (`1..5`) normalized to `0..100`.
- **Psychological safety group aggregate (`group.psychological_safety_aggregate`)**: mean of available per-person psych safety scores.
- **Conflict style profile**: if user enters raw mode scores, normalize each mode by total:  
  `mode_pct = ROUND(100 * mode_raw / SUM(all_5_modes_raw), 0)`; if total = 0, set all modes missing.
- **Attachment profile**: same proportional normalization as conflict style when raw entries are not already percentages.
- **Relationship health score (directed pair)**:  
  `rel.health = ROUND(0.25*rel.trust + 0.20*rel.respect + 0.15*rel.communication_frequency + 0.15*rel.emotional_closeness + 0.10*(100-rel.conflict_intensity) + 0.10*(100-rel.avoidance) + 0.05*(100-rel.power_differential), 0)`.
- **Missing-data handling**:
  - Use null/blank for unknown values; never coerce missing to zero.
  - For computed composites, compute weighted mean over available components only.
  - If fewer than 60% of required inputs for a composite are present, mark composite as missing and emit a `missing_data_flag=true` marker in output rows.
  - Include per-field confidence labels (`validated`, `self_report`, `observed`, `inferred`, `missing`) and propagate weakest confidence to each composite summary section.

#### 3) Frozen Artifact: Prompt I/O Spec

Prompt generator must output this exact block structure:

```text
=== SIMULATION_PROMPT_BEGIN ===
version: phase1_contract_v1
run_id: {{sim.run_id}}
group_id: {{group.id}}
scenario_id: {{scenario.id}}

[CONFIG]
{{JSON: sim.* fields by stable ID}}

[PEOPLE]
{{JSON array: one object per person keyed by stable IDs}}

[RELATIONSHIPS]
{{JSON array: directed edge objects keyed by rel.* stable IDs}}

[GROUP_CONTEXT]
{{JSON object keyed by group.* stable IDs}}

[SCENARIO]
{{JSON object keyed by scenario.* stable IDs}}

[OUTPUT_REQUIREMENTS]
Return one JSON object that exactly matches the schema in this contract.
No markdown. No prose outside JSON.
=== SIMULATION_PROMPT_END ===
```

Expected simulation output object schema:

```json
{
  "run_id": "string",
  "scenario_id": "string",
  "generated_at_utc": "ISO-8601 datetime",
  "outcome_clusters": [
    {
      "cluster_id": "string",
      "label": "string",
      "probability": "number 0..1",
      "narrative": "string",
      "key_drivers": ["stable field IDs or derived factors"],
      "early_signals": ["string"],
      "confidence": "number 0..1"
    }
  ],
  "individual_forecasts": [
    {
      "person_id": "string",
      "likely_behaviors": ["string"],
      "stress_response": "string",
      "influence_on_others": "string",
      "confidence": "number 0..1"
    }
  ],
  "interventions": [
    {
      "intervention_id": "string",
      "description": "string",
      "target_level": "individual|dyad|group|leader",
      "expected_effect": "string",
      "risk": "string",
      "estimated_impact": "number 0..1"
    }
  ],
  "evidence_coverage": {
    "missing_field_ids": ["string"],
    "coverage_ratio": "number 0..1",
    "overall_confidence": "number 0..1"
  },
  "limitations": ["string"]
}
```

#### Contract acceptance criteria

- Contract considered locked when one full synthetic run executes without manual prompt editing.

### Phase 1 Gate Milestones

Gate sequencing rule: **Gate D is blocked until Gate C has deterministic prompt structure output** (same section order, headings, and key names across repeated exports for unchanged inputs).

| Gate | Scope | Definition of Done | Required artifacts |
|------|-------|--------------------|--------------------|
| **Gate A — People + Assessments + Validation Rules** | People tab and all per-person assessment tabs, including validation behavior and scoring formulas. | 1) People tab supports stable IDs, role metadata, active flags, and cross-tab lookup references.<br>2) Big Five, Conflict Style, Psychological Safety, Communication/Decision, EQ, and optional Attachment inputs are implemented with input constraints from the Phase 1 contract.<br>3) Validation catches required fields, range violations, and profile sum checks (Conflict and Attachment) with clear fail indicators.<br>4) Normalized/computed per-person outputs calculate without manual intervention for a 5-person synthetic dataset.<br>5) No unresolved validation errors remain in the Gate A sample workbook state. | - **Sheet version tag**: `phase1_gateA_v1` (or incremented patch version).<br>- **Sample data snapshot**: 5-person synthetic roster plus complete per-person assessments exported (CSV/XLSX snapshot).<br>- **Prompt version**: `N/A` (prompt block not yet accepted at this gate).<br>- **Run notes**: Gate A validation log (date, validator name, checks performed, defects found/fixed). |
| **Gate B — Relationship Matrix + Group/Scenario/Config** | Relationship Matrix, Group Context, Scenario Builder, and Simulation Config tabs with schema compliance. | 1) Directed relationship matrix is fully populated from valid `person.id` values and rejects self-links.<br>2) Relationship composite score formulas and missing-data behavior run per contract.<br>3) Group Context fields and Scenario Builder fields enforce required fields and bounds.<br>4) Simulation Config fields enforce allowed enum/range values and produce a valid `sim.run_id`.<br>5) All Gate A and Gate B tabs pass contract-level validation in one integrated workbook check. | - **Sheet version tag**: `phase1_gateB_v1`.<br>- **Sample data snapshot**: Gate A dataset + complete relationship edges + one fully filled group/scenario/config set.<br>- **Prompt version**: `draft_prompt_v0` (schema-complete but not yet stability-approved).<br>- **Run notes**: Gate B integration checklist with data integrity and validation outcomes. |
| **Gate C — Prompt Generation Block Stable + Copy/Paste Ready** | Prompt Inputs / output assembly layer, including exact block structure and deterministic formatting. | 1) Generated prompt matches the frozen Prompt I/O section order and heading labels exactly.<br>2) Prompt output is **deterministic in structure**: repeated generations from unchanged data produce identical structure (differences allowed only in fields intentionally time-varying such as `run_id` when regenerated).<br>3) Copy/paste into Claude requires no manual editing for delimiters, headers, JSON boundaries, or required sections.<br>4) Prompt includes all required entities (config, people, relationships, group context, scenario, output requirements) keyed by stable IDs.<br>5) A prompt QA checklist confirms structure validity on at least 3 consecutive exports. | - **Sheet version tag**: `phase1_gateC_v1`.<br>- **Sample data snapshot**: Gate B dataset frozen for prompt regression checks.<br>- **Prompt version**: `phase1_contract_v1_prompt` (or incremented compatible revision).<br>- **Run notes**: Determinism test log showing at least 3 repeated exports and structural comparison results. |
| **Gate D — End-to-End Validation (5-person synthetic team, >=3 scenario runs)** | Full simulation workflow from data entry to output logging, with quality review over multiple scenarios. | 1) **Entry criterion**: Gate C determinism is confirmed and documented.<br>2) One 5-person synthetic team dataset is run through at least 3 distinct scenario executions (or 3 runs with materially different scenario settings) using the Gate C prompt format.<br>3) Each run is logged with raw output, summarized outcomes, confidence, and limitations in Simulation Output Log.<br>4) Output review confirms structure compliance, evidence anchoring, and useful intervention recommendations across runs.<br>5) Post-run retrospective records prompt or schema refinements and whether Phase 1 contract stays frozen or needs revision. | - **Sheet version tag**: `phase1_gateD_v1`.<br>- **Sample data snapshot**: Final synthetic team workbook and scenario set used for validation.<br>- **Prompt version**: Locked Gate C prompt version identifier used in all runs.<br>- **Run notes**: End-to-end validation report containing at least 3 run records, findings, and change decisions. |

**Gate control policy**
- Do not start Gate D execution tasks until Gate C determinism evidence is present in run notes.
- If Gate C structure drifts after edits, reopen Gate C and pause Gate D until determinism is restored.
- Any schema-breaking prompt change requires a new prompt version and explicit note in the decision log.

### Phase 1 Tasks

#### 1.1 — Design & Specification
- [x] Read and understand full system design document
- [x] Create CLAUDE.md session context file
- [x] Create PLAN.md implementation plan
- [ ] Define exact field lists and validation rules for each tab (can be done in the spreadsheet itself)
- [ ] Define the normalized score computation rules (raw → 0–100 scale per domain)
- [ ] Define the confidence rating system (1–5 or categorical: Validated / Self-report / Observed / Inferred / Missing)

#### 1.2 — Spreadsheet Build: People and Roles
- [ ] Create People tab with columns: PersonID, DisplayName, Role, GroupMembership, AuthorityLevel, IsActive
- [ ] Create named range or dropdown for PersonID cross-referencing in other tabs
- [ ] Add README/Consent tab with instructions and ethical notes

#### 1.3 — Spreadsheet Build: Assessment Tabs
- [ ] **Big Five tab**: One block per person (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism). Raw score → normalized 0–100. Evidence source dropdown. Confidence rating.
- [ ] **Conflict Style tab**: Five-mode profile per person (Competing, Collaborating, Compromising, Avoiding, Accommodating). Normalized weights. Evidence source.
- [ ] **Psychological Safety tab**: Edmondson 7-item team survey. Per-person and group aggregate. Evidence source.
- [ ] **Communication & Decision Style tab**: Direct/indirect, high/low-context, verbal dominance, listening quality, feedback tolerance, analytical vs. intuitive, risk appetite, decision speed, ambiguity tolerance. Evidence source.
- [ ] **Emotional Intelligence tab**: Perceiving, using, understanding, managing emotions. Self-report + observation fields. Evidence source.
- [ ] **Attachment Tendencies tab** (optional in Phase 1 org mode): Secure, anxious, avoidant, fearful tendency ratings. Evidence source.

#### 1.4 — Spreadsheet Build: Relationship Matrix
- [ ] **Relationship Matrix tab**: Auto-populated person list from People tab. Directed pairwise fields: trust, influence, emotional closeness, respect, conflict intensity, dependency, communication frequency, avoidance, alliance/coalition, power differential. Evidence source per pair. Notes field.
- [ ] Add formula to compute aggregate relationship health score per pair and overall network health

#### 1.5 — Spreadsheet Build: Group and Scenario
- [ ] **Group Context tab**: Group type, formal/informal structure, shared goals, explicit/implicit norms, psychological safety aggregate, decision rules, conflict/cohesion history, current stress level, role clarity, cultural context, environmental constraints
- [ ] **Scenario Builder tab**: Title, type, triggering event description, stakes level (1–5), emotional intensity (1–5), ambiguity level (1–5), time pressure (1–5), resource constraints, public visibility flag, required decision description, success criteria, failure consequences, known facts list, uncertain facts list, intervention options to test

#### 1.6 — Spreadsheet Build: Simulation Config
- [ ] **Simulation Config tab**: Number of passes (1–10), randomness setting (Low/Medium/High), simulation depth (Surface/Standard/Deep), dialogue enabled (Y/N), report detail level (Summary/Standard/Full), intervention testing mode (Baseline/Compare), source evidence strictness (Strict/Moderate/Lenient), guardrail verbosity (Minimal/Standard/Verbose)

#### 1.7 — Spreadsheet Build: Profile Output & Prompt Generation
- [ ] **Structured Profile Output tab**: Computed summary view pulling from all assessment tabs. Formatted for human review. Shows: person name, role, OCEAN summary (high/medium/low per trait), dominant conflict mode, primary communication patterns, decision style summary, EQ summary, attachment tendency, key motivations/values/triggers. Confidence rating per section. Missing data flags.
- [ ] **Prompt Inputs tab**: Formula-generated prompt block. Assembles system prompt, person profile blocks, relationship data block, group context block, scenario block, config block, and output format instructions. Single cell with full concatenated prompt ready to copy-paste into Claude.

#### 1.8 — Spreadsheet Build: Output Logging
- [ ] **Simulation Output Log tab**: Table with columns: RunID, Date, ScenarioTitle, PassNumber, RawOutput (paste area), OutcomeClassification, ProbabilityEstimate, ConfidenceEstimate, KeyFindings, Recommendations, LimitationNotes, ReviewedBy. Auto-generate RunID from timestamp.

#### 1.9 — Spreadsheet Build: Visuals
- [ ] **Visuals tab**: Relationship trust heat map (matrix visualization using conditional formatting), Influence map (sorted bar chart), OCEAN radar charts per person, Conflict style stacked bar per person, Outcome cluster distribution chart (manual input from simulation log)

#### 1.10 — Prompt Engineering
- [ ] Draft System Role prompt for the simulator agent
- [ ] Draft Person Profile block template (one block per person)
- [ ] Draft Relationship block template
- [ ] Draft Group Context block template
- [ ] Draft Scenario block template
- [ ] Draft Output Format instructions block (aligned with Simulation Output Object schema)
- [ ] Draft Evaluator prompt (consistency, plausibility, evidence alignment check)
- [ ] Test prompt with synthetic team data (3-person team, simple scenario)
- [ ] Test prompt with realistic team data (5–8 person team, complex scenario)
- [ ] Iterate until output structure is consistent and evidence-anchored

#### 1.11 — End-to-End Validation
- [ ] Create a sample dataset: fictional 5-person leadership team
- [ ] Enter full dataset into spreadsheet
- [ ] Generate prompt from Prompt Inputs tab
- [ ] Run simulation in Claude (2–3 passes)
- [ ] Log output in Simulation Output Log
- [ ] Review output quality: narrative plausibility, evidence anchoring, probability weights, intervention recommendations
- [ ] Refine prompt and/or spreadsheet structure based on findings
- [ ] Document what worked and what needs adjustment in this file

---

## Phase 2 — Web Application

**Prerequisite**: Phase 1 prompt model validated. Clear understanding of data model, prompt structure, and output format.

**Goal**: Replace the spreadsheet with a proper web application backed by a database. Users can manage multiple groups, scenarios, and simulation runs through a UI.

**Recommended stack** (to be confirmed before build):
- Backend: Python / FastAPI
- Database: PostgreSQL (with SQLAlchemy ORM)
- Frontend: React + TypeScript (Vite)
- AI integration: Anthropic Claude API (claude-opus-4-7 or claude-sonnet-4-6)
- Visualization: D3.js or Recharts

### Phase 2 Tasks (High Level — Detail when Phase 1 complete)

#### 2.1 — Architecture & Setup
- [ ] Confirm tech stack
- [ ] Design database schema (mapped from spreadsheet data model)
- [ ] Set up project scaffolding (backend, frontend, database)
- [ ] Set up local development environment
- [ ] Define API contract (OpenAPI spec)

#### 2.2 — Core Data Model Implementation
- [ ] Person Profile CRUD (API + UI)
- [ ] Relationship Matrix CRUD (API + UI)
- [ ] Group Profile CRUD (API + UI)
- [ ] Scenario Profile CRUD (API + UI)
- [ ] Simulation Config CRUD (API + UI)

#### 2.3 — Assessment Administration
- [ ] Big Five assessment form (per person)
- [ ] Conflict Style assessment form (per person)
- [ ] Psychological Safety survey (group)
- [ ] Communication & Decision Style form (per person)
- [ ] Score computation and normalization
- [ ] Evidence source and confidence tracking

#### 2.4 — Simulation Engine
- [ ] Prompt assembly service (takes DB records → structured prompt)
- [ ] Claude API integration (multi-pass simulation runner)
- [ ] Evaluator pass integration
- [ ] Simulation output parser and storage
- [ ] Run history and versioning

#### 2.5 — Report Generation
- [ ] Report template engine (sections from design doc)
- [ ] Probability-weighted outcome cluster display
- [ ] Individual behavior forecast display
- [ ] Intervention recommendation section
- [ ] Limitations and ethics warning section
- [ ] Export to PDF/Markdown

#### 2.6 — Visualization
- [ ] Relationship network graph (D3.js force-directed)
- [ ] Trust/conflict heat map
- [ ] Influence ranking chart
- [ ] OCEAN radar chart per person
- [ ] Outcome cluster probability chart

#### 2.7 — Intervention Lab (Phase 2 stretch)
- [ ] Baseline vs. intervention comparison runner
- [ ] Intervention option selector
- [ ] Side-by-side outcome comparison view

---

## Phase 3 — Transcript & Notes Ingestion

**Prerequisite**: Phase 2 complete and stable.

- [ ] Meeting transcript parser (extract behavioral evidence)
- [ ] Communication pattern analyzer
- [ ] Sentiment and conflict marker extraction
- [ ] Quote bank with evidence tracebacks
- [ ] Map extracted evidence to profile fields with confidence ratings

---

## Phase 4 — Intervention Lab (Full)

**Prerequisite**: Phase 3 complete.

- [ ] Coaching script generator
- [ ] Facilitation plan generator
- [ ] Scenario replay with modified parameters
- [ ] Outcome probability shift analysis after intervention

---

## Phase 5 — Research Workspace

**Prerequisite**: Phase 4 complete.

- [ ] Case library (named, versioned group profiles)
- [ ] Simulation run history with search and filter
- [ ] Cross-case pattern analysis
- [ ] Exportable research notes
- [ ] Framework comparison mode (run same scenario with different psychological frameworks)


## Run Ledger

Record one row **for each completed simulation trial**.

| RunID | Dataset Used | Prompt Version | Model/Version | Key Outcome Quality Notes | Decision Taken |
|---|---|---|---|---|---|
| _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

### End-of-Session Update Checklist (<= 5 minutes)

1. Add/complete Run Ledger rows for all trials finished this session.
2. Ensure each row includes: dataset, prompt version, model/version, quality notes, and explicit decision.
3. Update relevant Phase task checkboxes based on what was completed.
4. Add/refresh any blockers or open questions created by the trial outcomes.
5. Confirm `CLAUDE.md` Session Handoff was updated in the same session.

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-24 | Start with Excel/Google Sheets prototype before web app | Validate psychological model and prompt design before investing in software |
| 2026-04-24 | Focus Phase 1 on organizational teams only | Clearer roles, less clinical risk than family-system modeling; aligns with design doc MVP recommendation |
| 2026-04-24 | Use Tiers 1–4 of framework stack as modeling engine; Tier 5 as interpretive overlay only | Prevents pseudoscience; anchors outputs to evidence |
| 2026-04-24 | Hybrid multi-agent simulation approach (not pure LLM roleplay) | Keeps AI anchored to structured data, prevents drift and stereotyping |

---

## Notes / Open Questions

- **Spreadsheet format**: Google Sheets preferred for formula power and sharability, but Excel (.xlsx) can be generated programmatically and version-controlled. Decide before building.
- **Prompt format**: Should prompt blocks be JSON, YAML, or structured natural language? JSON is machine-parseable; natural language may produce better simulation quality. Hybrid likely best — natural language narrative wrapping JSON data blocks.
- **Evidence confidence scale**: Design doc mentions 1–5 numeric or categorical labels (Validated/Self-report/Observed/Inferred/Missing). Categorical is clearer for users; can map to numeric for computations.
- **OCEAN scoring**: Design doc recommends IPIP-based Big Five (50-item or 120-item). In Phase 1, allow manual score entry (pre-computed from any validated instrument) rather than administering the assessment in the spreadsheet.
- **Phase 2 stack confirmation**: Confirm Python/FastAPI vs. Node.js/Express before starting Phase 2. User preference matters here.
