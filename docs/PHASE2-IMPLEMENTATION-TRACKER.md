# PHASE 2 — IMPLEMENTATION TRACKER

> Operational tracker for sprint execution. Keep statuses current at least weekly.

## Sprint Board

### Backlog

- [ ] **DM-03: Add scenario versioning to core entities**
  - **Workstream:** Data model
  - **Owner:** [ ]
  - **Estimate:** [ ] (S/M/L or points)
  - **Dependency:** DM-01 finalized
  - **Acceptance criteria:**
    - [ ] Version field added to scenario aggregate
    - [ ] Backward compatibility migration documented
    - [ ] Read/write path supports latest + historical versions

- [ ] **API-03: Add simulation run export endpoint**
  - **Workstream:** API
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** API-01 auth middleware complete
  - **Acceptance criteria:**
    - [ ] `GET /runs/{id}/export` returns validated payload
    - [ ] Authorization checks enforced
    - [ ] Contract test coverage added

- [ ] **UI-03: Build run comparison view**
  - **Workstream:** UI
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** API-03 available
  - **Acceptance criteria:**
    - [ ] User can select 2+ runs and compare key metrics
    - [ ] Empty/loading/error states implemented
    - [ ] Accessibility checks pass for controls and tables

- [ ] **PE-03: Add deterministic seed controls**
  - **Workstream:** Prompt engine
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** DM-03 merged
  - **Acceptance criteria:**
    - [ ] Seed configurable per run
    - [ ] Repeated run with same seed yields stable outputs within tolerance
    - [ ] Seed included in run metadata

- [ ] **QA-03: Create regression suite for phase-2 critical paths**
  - **Workstream:** QA/validation
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** API-03 + UI-03 test hooks available
  - **Acceptance criteria:**
    - [ ] Automated suite executes in CI
    - [ ] Baseline snapshots established
    - [ ] Failure triage runbook linked

- [ ] **DOC-03: Publish phase-2 operator handbook updates**
  - **Workstream:** Docs
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** UI-03 behavior finalized
  - **Acceptance criteria:**
    - [ ] Setup + usage sections updated
    - [ ] Troubleshooting FAQ added
    - [ ] Cross-links to API reference verified

### In Progress

- [ ] **DM-02: Normalize actor interaction schema**
  - **Workstream:** Data model
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** DM-01 entity IDs stabilized
  - **Acceptance criteria:**
    - [ ] Interaction schema in place and migrated
    - [ ] Integrity constraints enforced
    - [ ] Existing data migrated with no loss

- [ ] **API-02: Add run status polling + pagination**
  - **Workstream:** API
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** API-01 auth middleware complete
  - **Acceptance criteria:**
    - [ ] Status endpoint returns queued/running/completed/failed
    - [ ] Pagination implemented and documented
    - [ ] Load test meets agreed latency threshold

- [ ] **UI-02: Implement run timeline and status indicators**
  - **Workstream:** UI
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** API-02 status payload stable
  - **Acceptance criteria:**
    - [ ] Timeline reflects backend states accurately
    - [ ] Polling/backoff strategy implemented
    - [ ] UX review approved

- [ ] **PE-02: Prompt template modularization**
  - **Workstream:** Prompt engine
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** DM-02 schema finalized
  - **Acceptance criteria:**
    - [ ] Templates decomposed into reusable modules
    - [ ] Runtime composition path covered by tests
    - [ ] Prompt diff snapshots updated

- [ ] **QA-02: Define golden-set validation checks**
  - **Workstream:** QA/validation
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** PE-02 merged
  - **Acceptance criteria:**
    - [ ] Golden-set cases documented
    - [ ] Threshold assertions codified
    - [ ] CI job posts summary artifact

- [ ] **DOC-02: Draft release notes + migration checklist**
  - **Workstream:** Docs
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** DM-02 + API-02 locked
  - **Acceptance criteria:**
    - [ ] User-facing changes listed
    - [ ] Migration steps validated by dry run
    - [ ] Review sign-off captured

### Blocked

- [ ] **DM-01: Finalize canonical entity IDs**
  - **Workstream:** Data model
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** External identity mapping decision
  - **Acceptance criteria:**
    - [ ] ID scheme approved by architecture review
    - [ ] Collision strategy documented
    - [ ] Seed data regenerated successfully

- [ ] **API-01: Standardize auth middleware behavior**
  - **Workstream:** API
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** DM-01 complete
  - **Acceptance criteria:**
    - [ ] Auth behavior consistent across endpoints
    - [ ] Unauthorized/forbidden responses standardized
    - [ ] Security tests pass

- [ ] **UI-01: Consolidate global navigation shell**
  - **Workstream:** UI
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** API-01 auth route guards complete
  - **Acceptance criteria:**
    - [ ] Navigation reflects role-based access
    - [ ] Route guard redirects validated
    - [ ] Keyboard navigation passes audit

- [ ] **PE-01: Baseline system-prompt policy alignment**
  - **Workstream:** Prompt engine
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** Product policy sign-off
  - **Acceptance criteria:**
    - [ ] Policy constraints encoded in prompt scaffolding
    - [ ] Unsafe output checks integrated
    - [ ] Review checklist completed

- [ ] **QA-01: CI environment parity fixes**
  - **Workstream:** QA/validation
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** Infrastructure secrets provisioning
  - **Acceptance criteria:**
    - [ ] CI uses production-like config profile
    - [ ] Flaky tests reduced below threshold
    - [ ] Repeatability verified for 3 consecutive runs

- [ ] **DOC-01: Define doc ownership matrix**
  - **Workstream:** Docs
  - **Owner:** [ ]
  - **Estimate:** [ ]
  - **Dependency:** Team staffing confirmation
  - **Acceptance criteria:**
    - [ ] Each critical doc has DRI + backup
    - [ ] Review cadence documented
    - [ ] Escalation path published

### Done

- [ ] *(Move completed tasks here and stamp date.)*
  - Example format:
  - [x] `TASK-ID` — task title (**Workstream:** ..., **Owner:** ..., **Done date:** YYYY-MM-DD)

---

## Workstream Index (Quick Filter)

- **Data model:** DM-01, DM-02, DM-03
- **API:** API-01, API-02, API-03
- **UI:** UI-01, UI-02, UI-03
- **Prompt engine:** PE-01, PE-02, PE-03
- **QA/validation:** QA-01, QA-02, QA-03
- **Docs:** DOC-01, DOC-02, DOC-03

---

## Risk Register

| ID | Risk | Impact | Likelihood | Trigger threshold | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R1 | Data model changes break backward compatibility | High | Medium | >2 migration failures in staging in a week | Add contract tests + dry-run migrations on snapshots before merge | [ ] | Open |
| R2 | API latency regression under polling load | High | Medium | p95 latency > 800ms for 2 consecutive daily runs | Add caching, tune query paths, enforce pagination limits | [ ] | Open |
| R3 | UI status drift from backend state | Medium | Medium | >3 mismatches found in QA golden scenarios | Introduce shared status enum + integration assertions | [ ] | Open |
| R4 | Prompt output quality instability | High | Medium | Validation pass rate < 90% over rolling 20-run window | Lock template versions, seed controls, broaden golden set | [ ] | Open |
| R5 | CI instability blocks release confidence | High | Medium | Flake rate > 5% over last 50 CI jobs | Quarantine flaky tests, fix env parity, enforce rerun diagnostics | [ ] | Open |
| R6 | Documentation lag causes support load | Medium | High | >5 recurring support questions/week on unchanged flows | Publish owner matrix, weekly doc review, release note checklist | [ ] | Open |

---

## Weekly Async Status Template

> Copy this section into the team status channel every week.

### Week of: YYYY-MM-DD

- **Overall RAG:** [ ] Green [ ] Amber [ ] Red
- **Top 3 priorities (this week):**
  - [ ]
  - [ ]
  - [ ]
- **Completed since last update:**
  - [ ]
- **In progress now:**
  - [ ]
- **New blockers/escalations:**
  - [ ]
- **Risk changes (new/raised/lowered):**
  - [ ]
- **Metric snapshot:**
  - [ ] API p95 latency: ___ ms
  - [ ] Prompt validation pass rate: ___ %
  - [ ] CI flake rate: ___ %
  - [ ] Open defects (sev1/sev2): ___ / ___
- **Decisions needed by:**
  - [ ] YYYY-MM-DD — decision + owner
- **Plan for next week:**
  - [ ]

---

## Tracker Maintenance Rules

- [ ] Update task status changes within 24h.
- [ ] Ensure every active task has owner + estimate filled.
- [ ] If blocked > 3 business days, add escalation owner/date.
- [ ] Keep acceptance criteria binary and testable.
- [ ] Archive closed risks monthly and add new IDs sequentially.
