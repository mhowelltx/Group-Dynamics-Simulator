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

### Phase 1 — Spreadsheet Prototype (CURRENT)
A Google Sheets / Excel workbook that transforms assessment data into structured, model-ready variables and generates AI prompts. Goal: validate the psychological model and prompt design before building software.

**Branch**: `claude/plan-group-simulator-5kmcc`
**Status**: Planning complete. Spreadsheet not yet built.

### Phase 2 — Web Application
Web UI + database backend replacing the spreadsheet. Built after the prompt model is validated.

**Branch**: TBD (create from main when ready)
**Stack**: TBD — design doc is stack-agnostic; recommend Python/FastAPI + PostgreSQL + React

---

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

## Data Model Objects (Phase 1 Scope)

- **Person Profile** — OCEAN scores, conflict style, EQ, communication style, decision style, stress response, motivations, values, evidence sources
- **Relationship Profile** — Directed matrix: trust, influence, emotional closeness, conflict intensity, power differential, alliance indicators
- **Group Profile** — Type, structure, norms, psychological safety, decision rules, stress level, cultural context
- **Scenario Profile** — Triggering event, stakes, emotional intensity, time pressure, success/failure criteria
- **Simulation Config** — Passes, randomness, depth, dialogue on/off, strictness settings
- **Simulation Output** — Timeline, behavior traces, outcome clusters, probability weights, recommendations

---

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
2. Read `PLAN.md` — check current phase status and next tasks
3. Check which phase is active and what's been completed
4. Read the relevant section of the design doc if working on a new component
5. Continue from the first incomplete task in PLAN.md

---

## Important Constraints

- Personal use only — no multi-tenant, no PII data store requirements in MVP
- Not a clinical tool, not a hiring tool, not a legal tool
- All outputs must carry confidence ratings and evidence tracebacks
- All outputs must include limitation and ethics warnings
- Family-system modeling is Phase 2+ — Phase 1 focuses on organizational teams
- No automated assessment administration in Phase 1

## Session Handoff

Use this section at the **end of every work session** to leave clear continuity for the next session.

- **Current milestone**: Phase 1.10 prompt trial artifacts generated for synthetic (3-person) and realistic (5-person) scenarios with deterministic structure checks.
- **Last completed task ID**: 1.10.h-i (`scripts/prompt_trial_runner.py` implemented and artifacts generated in `artifacts/prompt_trials/`)
- **Next 3 concrete tasks**:
  1. Execute model-in-the-loop Claude run for the 3-person trial prompt and score all five rubric dimensions.
  2. Execute model-in-the-loop Claude run for the 5-person trial prompt and compare quality vs baseline prompt key.
  3. Iterate prompt wording based on rubric deltas; only promote prompt version after >=3 comparable improvements.
- **Known blockers**:
  - Manual workbook validation still required (open the .xlsx, check formulas evaluate correctly, confirm conditional formatting and list validations fire on bad data).
  - Gate C DoD evidence (determinism log + checklist) not yet recorded in `PLAN.md`.
- **Open decisions with owner/date**:

| Decision | Owner | Target date | Status |
|---|---|---|---|
| Choose spreadsheet platform (Google Sheets vs Excel) | Project owner | 2026-04-26 | **Resolved** — Excel (.xlsx) via build script; import to Google Sheets for sharing if needed |
| Choose prompt packaging format default (JSON-heavy vs hybrid narrative+JSON) | Project owner | 2026-04-27 | Open |
| Choose confidence representation default (categorical vs numeric-visible) | Project owner | 2026-04-27 | **Resolved** — categorical (validated/self_report/observed/inferred/missing) locked in contract |

### End-of-Session Update Checklist (<= 5 minutes)

1. Update `CLAUDE.md` Session Handoff fields (milestone, last completed task, next 3 tasks, blockers, open decisions).
2. Update `PLAN.md` Run Ledger with any simulation trials completed this session.
3. Mark task checkboxes in `PLAN.md` for any tasks completed this session.
4. Add one dated note in `PLAN.md` describing key outcome quality and decision taken.
5. Save both files and run `git diff -- CLAUDE.md PLAN.md` to confirm continuity updates are present.
