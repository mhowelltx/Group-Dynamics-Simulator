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
