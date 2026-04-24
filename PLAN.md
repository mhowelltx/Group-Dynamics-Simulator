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
