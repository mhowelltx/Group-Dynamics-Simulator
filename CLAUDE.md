# Group Dynamics Simulator — Claude Session Context

This file is the persistent context for Claude Code sessions working on this project. Read it at the start of every session before taking any action.

---

## Project Overview

A personal-use, AI-assisted group dynamics simulator that models how groups behave under different scenarios. It is designed for coaching, reflection, research, and experimental exploration — not for clinical diagnosis, hiring, or legal decisions.

**Core capability**: Given structured psychological profiles, relationship data, and a scenario, simulate probable group dynamics, conflict patterns, decision trajectories, and intervention effectiveness — with probability-weighted outcomes and evidence-traced confidence levels.

## Key Design Documents

| File | Purpose |
|------|---------|
| `Goup Dynamics Simulator - High-Level System Design.md` | Full system design (760 lines) — primary reference |
| `PLAN.md` | Phased implementation plan with task tracking |
| `CLAUDE.md` | This file — session context and continuity |

---

## Implementation Phases

### Phase 1 — Spreadsheet Prototype (COMPLETED)
Phase 1 established and validated the spreadsheet-first contract artifacts (field dictionary, prompt contract, and run ledger workflow). Treat this as historical baseline context and do not expand Phase 1 scope unless explicitly doing maintenance/backfill.

**Branch**: `claude/plan-group-simulator-5kmcc`
**Status**: ✅ Complete (historical reference only)

### Phase 2 — Web Application (CURRENT)
Build the canonical web application and data layer that operationalize the Phase 1 contract in production-grade services.

**Branch**: TBD (create from main when implementation starts)
**Status**: 🚧 In progress (authoritative status tracked in `PLAN.md`)
**Stack direction**: TBD lock decision pending; design remains stack-agnostic until lock decision is made

## Active Branch Convention

```
claude/<short-description>-<5-char-id>
```

When starting a new session to continue work, check `git log --oneline -10` and `PLAN.md` to orient before making changes.

---

## Psychological Framework Stack (Summary)

| Tier | Framework | Role |
|------|-----------|------|
| 1 | Big Five / OCEAN | Core personality prediction |
| 2 | Conflict style, EQ, Communication style, Decision style | Interaction behavior |
| 3 | Attachment theory, Family systems | Relational dynamics |
| 4 | Psychological safety, CVF, IPO model | Group/org dynamics |
| 5 | DISC, MBTI, TA | Interpretive language only — not scientific foundation |

**Design rule**: Tiers 1–4 are the modeling engine. Tier 5 is optional communication overlay.

---

## Three-Layer Separation (Critical Design Principle)

The simulator must maintain strict separation of:
1. **Evidence Layer** — What is known from assessments, observations, notes
2. **Inference Layer** — What is reasonably estimated from the evidence
3. **Simulation Layer** — What may happen in a specific scenario

Never collapse these layers. Confidence ratings propagate through all outputs.

---

## Canonical Data Model Entities (Phase 2 Scope)

Use these entities as the canonical model for implementation work and validation against planning artifacts:

- **Person** — stable identity + role/authority metadata for each participant
- **AssessmentSnapshot** — timestamped assessment/observation values (OCEAN, conflict, EQ, communication, decision, attachment, psych safety items)
- **RelationshipEdge** — directed dyadic metrics (`from_person_id` → `to_person_id`) with per-edge evidence metadata
- **GroupContext** — group-level structure, norms, stress, decision context, and environment constraints
- **Scenario** — simulated situation definition including triggers, stakes, constraints, and success/failure criteria
- **SimulationConfig** — run-time controls (passes, randomness, depth, strictness, verbosity) and `prompt_version_key`
- **SimulationRun** — lineage object tying inputs/config/timestamps/output artifacts for each run
- **Evaluation fields** — rubric and quality fields (evidence anchoring, consistency, plausibility, intervention usefulness, uncertainty quality, aggregate scores/notes)

**Contract note**: Derived prompt artifacts (assembled prompt text blocks, convenience summaries, formatting composites) are non-canonical by default. Persist source-of-truth inputs and lineage metadata, then regenerate derived artifacts deterministically when needed.

## Spreadsheet Tab Plan (Phase 1)

| # | Tab Name | Purpose |
|---|----------|---------|
| 1 | README / Consent | Instructions, ethical notes, consent reminders |
| 2 | People | Name, role, group membership, authority level |
| 3 | Big Five Assessment | OCEAN input per person |
| 4 | Conflict Style Assessment | Five-mode conflict profile per person |
| 5 | Psychological Safety | Edmondson-style group survey |
| 6 | Communication & Decision Style | Structured fields per person |
| 7 | Emotional Intelligence | Self-report + observation fields |
| 8 | Attachment Tendencies | Secure/anxious/avoidant/fearful ratings |
| 9 | Relationship Matrix | Directed pairwise ratings |
| 10 | Group Context | Group-level fields |
| 11 | Scenario Builder | Scenario profile fields |
| 12 | Simulation Config | Pass count, randomness, depth, etc. |
| 13 | Structured Profile Output | Computed summary view — feeds prompts |
| 14 | Prompt Inputs | Generated prompt blocks ready to paste into AI |
| 15 | Simulation Output Log | Paste-back area for AI responses, with run metadata |
| 16 | Visuals | Charts: relationship graph, heat maps, outcome distribution |

---

## Simulation Prompt Architecture (Phase 1 Goal)

The spreadsheet must produce a **structured prompt block** that includes:

```
SYSTEM ROLE: You are a group dynamics simulator anchored to structured psychological profile data...

PERSON PROFILES: [structured OCEAN + conflict + EQ + communication + decision blocks per person]

RELATIONSHIP DATA: [directed matrix with trust/influence/conflict/power per pair]

GROUP CONTEXT: [psychological safety, norms, structure, stress level]

SCENARIO: [triggering event, stakes, time pressure, ambiguity, decision required]

SIMULATION CONFIG: [passes, randomness, depth, dialogue on/off]

INSTRUCTIONS: Run [N] simulation passes. For each pass:
1. Individual private appraisal
2. First public response
3. Interaction sequence
4. Conflict/stabilization update
5. Decision or non-decision point
6. Outcome classification
7. Evidence consistency review

OUTPUT FORMAT: [structured output spec per the Output Object schema]
```

---

## Output and Report Requirements

**Tone**: Academic-consultant (cautious, probabilistic, evidence-traced)
**Required language**: "The simulation suggests…", "A plausible pattern is…", "Confidence is limited because…"
**Forbidden language**: "This person will…", "This proves…", "The correct intervention is…"
**Mandatory sections in every simulation output**:
1. Confidence statement
2. Limitation statement
3. Non-determinism disclaimer
4. Evidence-vs-inference-vs-simulation separation check

Guardrail enforcement rule:
- If deterministic/diagnostic wording appears (for example: "will", "proves", "correct intervention is"), treat the run as failed.
- If any mandatory section is missing, treat the run as failed.
- Log each failed run in the `PLAN.md` **Guardrail Exceptions** table and refine prompt wording before the next run.

Report sections:
1. Executive Summary
2. Scenario and Data Inputs
3. Psychological Profile Summary
4. Relationship and Network Analysis
5. Simulation Method
6. Most Likely Narrative
7. Outcome Clusters (probability-weighted)
8. Individual Behavior Forecasts
9. System Dynamics Analysis
10. Intervention Recommendations
11. Visual Analytics
12. Limitations and Ethical Notes

---

## Session Startup Checklist

When starting a new session on this project:

1. `git log --oneline -10` — orient to recent commits
2. Read `PLAN.md` first — confirm current phase, active tasks, and sequencing (source of truth for status)
3. Confirm Phase 2 scope boundaries (do not re-open Phase 1 prototype tasks unless explicitly requested)
4. Read the relevant design-doc section before implementing a new subsystem (architecture intent first, then code)
5. Validate schema consistency against canonical entities (`Person`, `AssessmentSnapshot`, `RelationshipEdge`, `GroupContext`, `Scenario`, `SimulationConfig`, `SimulationRun`)
6. Verify `prompt_version_key` usage is explicit in any config/run path touched
7. Verify run lineage requirements are preserved (`run_id`, timestamps, config linkage, scenario/group linkage)
8. Continue from the first incomplete Phase 2 task in `PLAN.md`

## Important Constraints

- Personal use only — no multi-tenant, no PII data store requirements in MVP
- Not a clinical tool, not a hiring tool, not a legal tool
- All outputs must carry confidence ratings and evidence tracebacks
- All outputs must include limitation and ethics warnings
- Preserve explicit non-determinism in simulation language and outputs (never present outcomes as certainties)
- Family-system modeling is Phase 2+ — include only when the active Phase 2 task explicitly calls for it
- Derived prompt artifacts are **non-canonical**: persist source data + lineage, not redundant derived prompt blobs in core storage

### Cross-Document Source of Truth

- `PLAN.md` = implementation sequencing and status tracking
- `Goup Dynamics Simulator - High-Level System Design.md` = architecture intent and design rationale
- `CLAUDE.md` = session execution context and continuity protocol

## Session Handoff

Use this section at the **end of every work session** to leave clear continuity for the next session.

- **Current milestone**: Phase 2 Week 1 Foundation — complete. App boots, all routes return 200, integration tests pass.
- **Last completed task ID**: Full Phase 2 foundation build — models, schemas, routers, validation service, prompt builder, templates, main app. Branch: `claude/implement-phase-2-gy89c`.
- **Next 3 concrete tasks**:
  1. Add Phase 1 xlsx import CLI (`scripts/import_phase1.py`) that reads the spreadsheet and calls the validation layer before writing to the SQLite DB.
  2. Add run history filtering UI (filter by group, scenario, prompt version key) to `/simulations/` list view.
  3. Add integration test suite (`tests/`) covering: entity CRUD, validation sum checks, prompt builder determinism, and run lifecycle.
- **Known blockers**:
  - Auth boundary for personal-use MVP: currently none (localhost only). Confirm this is acceptable before adding any network exposure.
  - Migration approach from Phase 1 xlsx to canonical DB not yet implemented (import CLI is next task).
- **Open decisions with owner/date**:

| Decision | Owner | Target date | Status |
|---|---|---|---|
| Lock Phase 2 implementation stack (API framework, UI framework, DB tooling) | Project owner | 2026-04-25 | ✅ Resolved — FastAPI + SQLite + Jinja2 |
| Define MVP auth model (none/local-only/basic account) | Project owner | 2026-04-30 | Open — currently no auth (localhost only) |
| Confirm migration path from spreadsheet artifacts to canonical schema | Project owner | 2026-05-02 | Open — import CLI is next task |
| Finalize test strategy (unit/integration/e2e + simulation contract tests) | Project owner | 2026-05-03 | Open |

### End-of-Session Update Checklist (<= 5 minutes)

1. Update `CLAUDE.md` Session Handoff fields (milestone, last completed task, next 3 tasks, blockers, open decisions).
2. Update `PLAN.md` Run Ledger with any simulation trials completed this session.
3. Mark task checkboxes in `PLAN.md` for any tasks completed this session.
4. Add one dated note in `PLAN.md` describing key outcome quality and decision taken.
5. Save both files and run `git diff -- CLAUDE.md PLAN.md` to confirm continuity updates are present.
