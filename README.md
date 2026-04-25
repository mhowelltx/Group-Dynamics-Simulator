# Group-Dynamics-Simulator
AI-assisted group dynamics simulator for coaching, reflection, research, and experimental modeling of human interaction patterns.

## Build the Phase 1 workbook

The workbook generator is:

`scripts/build_workbook.py`

### Prerequisites

- Python 3.10+
- Python package dependencies installed:

```bash
python3 -m pip install -r requirements.txt
```

### Generate workbook

From the repo root:

```bash
python3 scripts/build_workbook.py
```

Expected output file:

`workbook/group-dynamics-simulator-phase1.xlsx`

The generated workbook includes Gate A–D support tabs:
- `Gate-A-Validation-Log`
- `Gate-B-Validation-Log`
- `Gate-C-Determinism-Log`
- `Gate-D-Run-Log`

## Run Phase 1.10 prompt trial artifacts

Generate deterministic prompt trial artifacts for:
- 3-person synthetic/simple scenario
- 5-person realistic/complex scenario

```bash
python3 scripts/prompt_trial_runner.py
```

Expected output folder:

`artifacts/prompt_trials/`

## GitHub Actions outputs

The `Build Workbook` workflow uploads two downloadable artifacts:
- `group-dynamics-simulator-phase1` → the generated workbook `.xlsx`
- `phase1-prompt-trials` → prompt trial markdown files + `determinism_report.json`

## Phase 2 Web App

### Scope (beyond the spreadsheet workflow)

Phase 2 introduces a production-style web application that replaces the single-workbook workflow with:
- Multi-group and multi-scenario data management in a persistent database.
- API-driven CRUD and validation for people, assessments, relationships, group context, scenarios, and simulation config.
- Reproducible run history, prompt/version lineage, and evaluator scoring as first-class backend records.
- Browser UI for data entry, simulation execution, and report/visualization consumption instead of manual copy/paste between tabs.

This scope aligns with the Phase 2 goals and task categories documented in `PLAN.md`.

### Proposed project structure (Phase 2)

The repository currently contains the Phase 1 workbook/scripts implementation. For Phase 2, add the following top-level layout to mirror the plan's backend + frontend + database split:

```text
web/                 # Frontend app (React + TypeScript/Vite once confirmed)
api/                 # Backend service (FastAPI once stack confirmed)
db/                  # Migrations, seeds, schema snapshots, local DB scripts
docs/                # API contract notes, architecture decisions, runbooks
```

Suggested substructure once scaffolding starts:

```text
api/
  app/
    routers/
    models/
    schemas/
    services/
    prompting/
  tests/
web/
  src/
    features/
    components/
    pages/
    lib/
  tests/
db/
  migrations/
  seeds/
docs/
  adr/
  api/
```

### Local development quickstart (to finalize with stack confirmation)

Use this as the Phase 2 quickstart template and replace placeholders immediately after stack/scaffolding is finalized:

```bash
# 1) Environment setup
cp .env.example .env
# fill in DB + model API keys

# 2) Start database (example)
docker compose up -d db

# 3) Backend
cd api
# e.g., python -m venv .venv && source .venv/bin/activate
# e.g., pip install -r requirements.txt
# e.g., uvicorn app.main:app --reload

# 4) DB migrate + seed
# e.g., alembic upgrade head
# e.g., python -m app.scripts.seed

# 5) Frontend
cd ../web
# e.g., npm install
# e.g., npm run dev
```

When Phase 2 starts, promote these example commands into exact, runnable commands for the chosen toolchain.

### Data contract and source-of-truth note

For Phase 2, treat the Phase 1 contract artifacts in `PLAN.md` as authoritative until superseded by an explicit contract revision entry:
- The frozen field dictionary (stable IDs, types, validation rules).
- The spreadsheet ↔ canonical model mapping section.

Any API schema, DB migration, importer, exporter, or UI form in Phase 2 must conform to those definitions.

### Phase 2 contribution guidance

#### 1) Adding fields without breaking the contract
- Do not rename or repurpose existing stable IDs.
- Additive changes only: add new fields as optional first, then tighten constraints in a documented migration path.
- Update `PLAN.md` contract tables and mapping notes in the same PR as schema changes.
- Include forward/backward compatibility notes for API payloads and persisted records.

#### 2) Prompt versioning expectations
- Treat prompt templates as versioned artifacts (e.g., `P<major>.<minor>` format).
- Bump minor for backward-compatible prompt refinements; bump major for breaking output-structure or rubric assumptions.
- Persist prompt version key on every run and keep change rationale in docs/PR notes.
- Never silently change prompt behavior without a version bump and regression comparison.

#### 3) Validation and test coverage for new endpoints
- Every new endpoint must enforce contract-level bounds/enums/required fields server-side (not UI-only).
- Add request/response schema tests and negative tests for invalid payloads.
- Add integration tests covering DB write/read round-trips and migration compatibility where applicable.
- For simulation-related endpoints, include deterministic fixture tests for prompt assembly/output parsing and run metadata persistence.
