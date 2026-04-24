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
| `sim.prompt_version_key` | Simulation Config / Log | string | semantic prompt key like `P1.0`, `P1.1` | Required; regex `^P[0-9]+\\.[0-9]+$` |
| `sim.passes` | Simulation Config | integer | `1..10` | Required |
| `sim.randomness` | Simulation Config | enum | `low`, `medium`, `high` | Required |
| `sim.depth` | Simulation Config | enum | `surface`, `standard`, `deep` | Required |
| `sim.dialogue_enabled` | Simulation Config | boolean | `true`, `false` | Required |
| `sim.report_detail_level` | Simulation Config | enum | `summary`, `standard`, `full` | Required |
| `sim.intervention_mode` | Simulation Config | enum | `baseline`, `compare` | Required |
| `sim.evidence_strictness` | Simulation Config | enum | `strict`, `moderate`, `lenient` | Required |
| `sim.guardrail_verbosity` | Simulation Config | enum | `minimal`, `standard`, `verbose` | Required |
| `eval.evidence_anchoring_score` | Simulation Output Log | integer | `1..5` | Required per run; evaluator rubric score |
| `eval.internal_consistency_score` | Simulation Output Log | integer | `1..5` | Required per run; evaluator rubric score |
| `eval.plausibility_score` | Simulation Output Log | integer | `1..5` | Required per run; evaluator rubric score |
| `eval.intervention_usefulness_score` | Simulation Output Log | integer | `1..5` | Required per run; evaluator rubric score |
| `eval.uncertainty_quality_score` | Simulation Output Log | integer | `1..5` | Required per run; evaluator rubric score |
| `eval.rubric_average_score` | Simulation Output Log | number | `1.0..5.0` | Computed mean of five rubric scores, rounded to 2 decimals |
| `eval.rubric_notes` | Simulation Output Log | string | free text | Optional evaluator comments (max 1000 chars) |

#### 1A) Mapping Doc — Spreadsheet ↔ Canonical Model

This section maps spreadsheet inputs/outputs to canonical entities so Phase 2 storage stays minimal and intentional.

**Legend**
- **Persistence**: `Persisted` means store in canonical DB/API model. `Spreadsheet-only (derived)` means compute in workbook/prompt layer and do not persist as first-class columns.
- **Nullability**: `Required` = non-null for valid record creation; `Nullable` = may be null when unknown/not collected.
- **Confidence/evidence metadata rules**:
  - Every persisted row should carry `evidence_source` (`validated`, `self_report`, `observed`, `inferred`, `missing`).
  - For composite/aggregated values, propagate weakest contributing evidence source and set `missing_data_flag=true` if required input coverage is <60%.
  - Maintain per-run lineage using `sim.run_id` + timestamped extraction context.

##### Person

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| People.`person.id` | `Person.id` | string | Required | Persisted | Source defaults to `validated` when ID regex/uniqueness checks pass. |
| People.`person.display_name` | `Person.display_name` | string | Required | Persisted | Use roster/admin source; do not infer. |
| People.`person.role` | `Person.role` | enum | Required | Persisted | Must be explicitly entered; inferred role must be labeled `inferred`. |
| People.`person.group_membership` | `Person.group_membership` | string | Required | Persisted | Tag source as roster vs manual entry. |
| People.`person.authority_level` | `Person.authority_level` | integer | Required | Persisted | Keep provenance from assessor/roster source. |
| People.`person.is_active` | `Person.is_active` | boolean | Required | Persisted | Operational/admin source. |

##### AssessmentSnapshot

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Big Five.* (`person.ocean.*`) | `AssessmentSnapshot.big_five_*` | integer (0..100) | Required for active person | Persisted | `self_report` unless instrument-admin verified (`validated`). |
| Conflict Style.* (`person.conflict.*`) | `AssessmentSnapshot.conflict_*` | integer (0..100) | Required | Persisted | Enforce sum rule; failed sum blocks `validated` status. |
| Psychological Safety items (`person.psych_safety.item_1..7`) | `AssessmentSnapshot.psych_safety_item_1..7` | integer (1..5) | Required when surveyed | Persisted | Keep item-level evidence source; default `self_report`. |
| Communication/Decision.* (`person.comm.*`, `person.decision.*`) | `AssessmentSnapshot.comm_*`, `AssessmentSnapshot.decision_*` | integer (0..100) | Nullable | Persisted | If estimated by coach/facilitator, mark `observed` or `inferred` explicitly. |
| EQ.* (`person.eq.*`) | `AssessmentSnapshot.eq_*` | integer (0..100) | Nullable | Persisted | Preserve instrument origin in metadata notes. |
| Attachment.* (`person.attachment.*`) | `AssessmentSnapshot.attachment_*` | integer (0..100) | Nullable | Persisted | If partial profile present, evidence cannot exceed weakest present field. |
| Computed person psych safety score | `AssessmentSnapshot.psych_safety_score` | integer (0..100) | Nullable | Spreadsheet-only (derived) | Derived from items; propagate weakest item evidence + coverage flag. |
| Computed normalized trait summaries | `AssessmentSnapshot.normalized_summary_json` | JSON/object | Nullable | Spreadsheet-only (derived) | Prompt-layer artifact; regenerate deterministically, do not persist to avoid bloat. |

##### RelationshipEdge

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Relationship Matrix.`rel.from_person_id` | `RelationshipEdge.from_person_id` | string (FK) | Required | Persisted | Must resolve to active `Person.id`. |
| Relationship Matrix.`rel.to_person_id` | `RelationshipEdge.to_person_id` | string (FK) | Required | Persisted | Must resolve; self-edge disallowed. |
| Relationship metrics (`rel.trust`..`rel.power_differential`) | `RelationshipEdge.*` matching metric names | integer (0..100) | Nullable | Persisted | Metric-level source can differ; aggregate uses weakest source. |
| Relationship Matrix.`rel.evidence_source` | `RelationshipEdge.evidence_source` | enum | Required | Persisted | Required at edge row level. |
| Relationship Matrix.`rel.notes` | `RelationshipEdge.notes` | string | Nullable | Persisted | If notes summarize inference, evidence source cannot be `validated`. |
| Computed relationship health (`rel.health`) | `RelationshipEdge.health_score` | integer (0..100) | Nullable | Spreadsheet-only (derived) | Calculated per scoring spec; not persisted as base column. |

##### GroupContext

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Group Context.`group.id` | `GroupContext.id` | string | Required | Persisted | `validated` once uniqueness/format checks pass. |
| Group Context core fields (`group.type`, `group.structure`, `group.shared_goals`, `group.decision_rules`, `group.conflict_history`, `group.stress_level`, etc.) | `GroupContext.*` | mixed (enum/string/int) | Mixed (required/nullable per contract) | Persisted | Mark each field with source: policy docs=`validated`, interview=`observed`/`self_report`. |
| `group.psychological_safety_aggregate` | `GroupContext.psychological_safety_aggregate` | integer (0..100) | Nullable | Spreadsheet-only (derived) | Aggregate from AssessmentSnapshot items; persist inputs, not aggregate column. |

##### Scenario

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Scenario Builder.`scenario.id` | `Scenario.id` | string | Required | Persisted | `validated` after ID checks. |
| Scenario Builder.`scenario.title`, `scenario.type`, `scenario.trigger_event`, `scenario.required_decision`, `scenario.success_criteria`, `scenario.failure_consequences` | `Scenario.*` | string/enum | Required | Persisted | Tag author and source basis (incident log vs hypothetical). |
| Scenario Builder pressure/stakes fields (`scenario.stakes_level`, `scenario.emotional_intensity`, `scenario.ambiguity_level`, `scenario.time_pressure`) | `Scenario.*` | integer (1..5) | Required | Persisted | If panel-calibrated, can be `validated`; otherwise `inferred`/`observed`. |
| Scenario Builder optional list fields (`scenario.known_facts`, `scenario.uncertain_facts`, `scenario.intervention_options`) | `Scenario.*` | array<string> | Nullable | Persisted | Keep citation/source note for each list block where possible. |

##### SimulationConfig

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Simulation Config.`sim.prompt_version_key` | `SimulationConfig.prompt_version_key` | string | Required | Persisted | Treated as configuration provenance anchor. |
| Simulation Config controls (`sim.passes`, `sim.randomness`, `sim.depth`, `sim.dialogue_enabled`, `sim.report_detail_level`, `sim.intervention_mode`, `sim.evidence_strictness`, `sim.guardrail_verbosity`) | `SimulationConfig.*` | int/enum/bool | Required | Persisted | Config is operational metadata; source is system/user selection (not inferred). |

##### SimulationRun

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Simulation Config / Log.`sim.run_id` | `SimulationRun.id` | string | Required | Persisted | Unique run lineage key. |
| Generated runtime timestamp | `SimulationRun.generated_at_utc` | datetime | Required | Persisted | System-generated `validated` metadata. |
| Foreign keys (`group.id`, `scenario.id`, config ref) | `SimulationRun.group_id`, `SimulationRun.scenario_id`, `SimulationRun.simulation_config_id` | string | Required | Persisted | Referential integrity enforced before run commit. |
| Prompt block text | `SimulationRun.prompt_payload` | text/json | Nullable | Spreadsheet-only (derived) | Store in logs/artifacts store only if needed; avoid core schema column bloat. |

##### SimulationPass

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Pass index (implicit from repeated pass outputs) | `SimulationPass.pass_index` | integer | Required | Persisted | Sequential within run; system-generated. |
| Pass-level model output JSON | `SimulationPass.output_json` | JSON | Required | Persisted | Evidence confidence comes from model output + coverage checks. |
| Pass-level evidence coverage (`missing_field_ids`, `coverage_ratio`, `overall_confidence`) | `SimulationPass.evidence_coverage_*` | array/number | Required | Persisted | Clamp confidence by weakest upstream source + missingness thresholds. |
| Intermediate formatting helpers | n/a | n/a | n/a | Spreadsheet-only (derived) | Keep only in workbook formulas; no API/DB fields. |

##### Recommendation

| Spreadsheet tab/field | Canonical entity.column | Data type | Nullability | Persistence | Confidence/evidence metadata rules |
|---|---|---|---|---|---|
| Simulation output `interventions[].intervention_id` | `Recommendation.id` | string | Required | Persisted | Stable ID from run output; uniqueness within run. |
| `interventions[].description` | `Recommendation.description` | string | Required | Persisted | Must map to output evidence; otherwise mark low confidence. |
| `interventions[].target_level` | `Recommendation.target_level` | enum | Required | Persisted | Controlled enum (`individual`, `dyad`, `group`, `leader`). |
| `interventions[].expected_effect`, `interventions[].risk` | `Recommendation.expected_effect`, `Recommendation.risk` | string | Required | Persisted | Text must remain linked to run/pass provenance. |
| `interventions[].estimated_impact` | `Recommendation.estimated_impact` | number (0..1) | Required | Persisted | Down-weight if evidence coverage ratio is low. |
| Post-hoc priority/rank helper columns | `Recommendation.rank` (optional future) | integer | Nullable | Spreadsheet-only (derived) | Ranking logic should be computed view-level until stable product requirement exists. |

**Schema bloat guardrails**
- Persist raw inputs, identifiers, run/pass outputs, and recommendation primitives.
- Keep workbook convenience composites, formatted prompt text blocks, and ad hoc ranking helpers as spreadsheet-only derived artifacts unless repeatedly needed by production queries.
- Promote a derived field to persisted only after proving cross-run analytical value and stable definition across prompt versions.

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
prompt_version_key: {{sim.prompt_version_key}}
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
Mandatory sections must be present in every run output:
1) confidence_statement
2) limitation_statement
3) non_determinism_disclaimer
4) evidence_inference_simulation_separation_check
If any mandatory section is missing, mark run_status="failed_guardrail" and log the failure in the Guardrail Exceptions table.
If deterministic or diagnostic wording appears (for example: "will", "proves", "correct intervention is"), mark run_status="failed_guardrail" and log the failure in the Guardrail Exceptions table.
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
  "confidence_statement": "string",
  "limitation_statement": "string",
  "non_determinism_disclaimer": "string",
  "evidence_inference_simulation_separation_check": {
    "evidence_only_claims": ["string"],
    "inference_claims": ["string"],
    "simulation_claims": ["string"],
    "mixing_detected": "boolean",
    "mixing_notes": ["string"]
  },
  "limitations": ["string"],
  "run_status": "ok|failed_guardrail"
}
```

#### 4) Frozen Artifact: Evaluation Rubric & Guardrail Enforcement

Evaluator rubric scoring (1–5 each) remains:
- Evidence anchoring
- Internal consistency
- Plausibility
- Intervention usefulness
- Uncertainty quality

**Hard guardrail checks (must pass for a run to be valid):**
1. Output includes all mandatory sections:
   - `confidence_statement`
   - `limitation_statement`
   - `non_determinism_disclaimer`
   - `evidence_inference_simulation_separation_check`
2. Separation check is explicit and complete:
   - Distinguishes evidence vs inference vs simulation claims.
   - Flags claim-mixing using `mixing_detected` and `mixing_notes`.
3. No deterministic or diagnostic wording in narrative, recommendations, or forecasts.
   - Fail-trigger examples include: `will`, `proves`, `correct intervention is`.
4. If any hard check fails:
   - Set `run_status=failed_guardrail`.
   - Do not count the run toward prompt promotion comparisons.
   - Add a row to the Guardrail Exceptions table with remediation notes.

#### Contract acceptance criteria

- Contract considered locked when one full synthetic run executes without manual prompt editing.

### Phase 1 Gate Milestones

Gate sequencing rule: **Gate D is blocked until Gate C has deterministic prompt structure output** (same section order, headings, and key names across repeated exports for unchanged inputs).
Prompt promotion rule: **Only promote to a new prompt version key (`P<major>.<minor>`) when the candidate prompt improves average evaluator rubric score on at least 3 comparable scenarios versus the current baseline prompt version.**

| Gate | Scope | Definition of Done | Required artifacts |
|------|-------|--------------------|--------------------|
| **Gate A — People + Assessments + Validation Rules** | People tab and all per-person assessment tabs, including validation behavior and scoring formulas. | 1) People tab supports stable IDs, role metadata, active flags, and cross-tab lookup references.<br>2) Big Five, Conflict Style, Psychological Safety, Communication/Decision, EQ, and optional Attachment inputs are implemented with input constraints from the Phase 1 contract.<br>3) Validation catches required fields, range violations, and profile sum checks (Conflict and Attachment) with clear fail indicators.<br>4) Normalized/computed per-person outputs calculate without manual intervention for a 5-person synthetic dataset.<br>5) No unresolved validation errors remain in the Gate A sample workbook state. | - **Sheet version tag**: `phase1_gateA_v1` (or incremented patch version).<br>- **Sample data snapshot**: 5-person synthetic roster plus complete per-person assessments exported (CSV/XLSX snapshot).<br>- **Prompt version**: `N/A` (prompt block not yet accepted at this gate).<br>- **Run notes**: Gate A validation log (date, validator name, checks performed, defects found/fixed). |
| **Gate B — Relationship Matrix + Group/Scenario/Config** | Relationship Matrix, Group Context, Scenario Builder, and Simulation Config tabs with schema compliance. | 1) Directed relationship matrix is fully populated from valid `person.id` values and rejects self-links.<br>2) Relationship composite score formulas and missing-data behavior run per contract.<br>3) Group Context fields and Scenario Builder fields enforce required fields and bounds.<br>4) Simulation Config fields enforce allowed enum/range values and produce a valid `sim.run_id`.<br>5) All Gate A and Gate B tabs pass contract-level validation in one integrated workbook check. | - **Sheet version tag**: `phase1_gateB_v1`.<br>- **Sample data snapshot**: Gate A dataset + complete relationship edges + one fully filled group/scenario/config set.<br>- **Prompt version**: `draft_prompt_v0` (schema-complete but not yet stability-approved).<br>- **Run notes**: Gate B integration checklist with data integrity and validation outcomes. |
| **Gate C — Prompt Generation Block Stable + Copy/Paste Ready** | Prompt Inputs / output assembly layer, including exact block structure and deterministic formatting. | 1) Generated prompt matches the frozen Prompt I/O section order and heading labels exactly.<br>2) Prompt output is **deterministic in structure**: repeated generations from unchanged data produce identical structure (differences allowed only in fields intentionally time-varying such as `run_id` when regenerated).<br>3) Copy/paste into Claude requires no manual editing for delimiters, headers, JSON boundaries, or required sections.<br>4) Prompt includes all required entities (config, people, relationships, group context, scenario, output requirements) keyed by stable IDs.<br>5) A prompt QA checklist confirms structure validity on at least 3 consecutive exports. | - **Sheet version tag**: `phase1_gateC_v1`.<br>- **Sample data snapshot**: Gate B dataset frozen for prompt regression checks.<br>- **Prompt version**: `phase1_contract_v1_prompt` (or incremented compatible revision).<br>- **Run notes**: Determinism test log showing at least 3 repeated exports and structural comparison results. |
| **Gate D — End-to-End Validation (5-person synthetic team, >=3 scenario runs)** | Full simulation workflow from data entry to output logging, with quality review over multiple scenarios. | 1) **Entry criterion**: Gate C determinism is confirmed and documented.<br>2) One 5-person synthetic team dataset is run through at least 3 distinct scenario executions (or 3 runs with materially different scenario settings) using the Gate C prompt format.<br>3) Each run is logged with raw output, summarized outcomes, confidence, limitations, `prompt_version_key`, and evaluator rubric scores in Simulation Output Log.<br>4) Output review confirms structure compliance, evidence anchoring, internal consistency, plausibility, uncertainty quality, and useful intervention recommendations across runs.<br>5) Post-run retrospective records prompt or schema refinements and whether Phase 1 contract stays frozen or needs revision.<br>6) Prompt version is promoted only if candidate average rubric score improves on at least 3 comparable scenarios versus baseline. | - **Sheet version tag**: `phase1_gateD_v1`.<br>- **Sample data snapshot**: Final synthetic team workbook and scenario set used for validation.<br>- **Prompt version**: Locked Gate C prompt version identifier used in all runs.<br>- **Run notes**: End-to-end validation report containing at least 3 run records, rubric comparisons, and change decisions. |

**Gate control policy**
- Do not start Gate D execution tasks until Gate C determinism evidence is present in run notes.
- If Gate C structure drifts after edits, reopen Gate C and pause Gate D until determinism is restored.
- Any schema-breaking prompt change requires a new prompt version and explicit note in the decision log.

---

### Gate A — Detailed Execution Plan

**Entry state**: Task 1.1 (design & specification) complete. No spreadsheet workbook exists yet.  
**Exit state**: All five DoD criteria for Gate A are satisfied; artifacts committed.  
**Blocking pre-requisite**: Platform decision (Google Sheets vs Excel) must be made before A.0 starts. Recommendation: **Google Sheets** — live formula evaluation, conditional-formatting-based validation indicators, real-time sharing, and no file-save cycle. Use Excel only if offline-first is required.

#### Gate A — Synthetic Team Specification

All Gate A tabs must be validated against this fixed 5-person fictional dataset. Use exactly these values; do not invent variations during Gate A.

**People**

| PersonID | DisplayName | Role | GroupMembership | AuthorityLevel | IsActive |
|---|---|---|---|---|---|
| `alex.rivera` | Alex Rivera | `leader` | Alpha Leadership Team | 5 | TRUE |
| `jordan.chen` | Jordan Chen | `manager` | Alpha Leadership Team | 4 | TRUE |
| `sam.okafor` | Sam Okafor | `manager` | Alpha Leadership Team | 4 | TRUE |
| `morgan.kim` | Morgan Kim | `ic` | Alpha Leadership Team | 2 | TRUE |
| `casey.walsh` | Casey Walsh | `advisor` | Alpha Leadership Team | 3 | TRUE |

**Big Five (OCEAN — direct 0..100 entry)**

| PersonID | Openness | Conscientiousness | Extraversion | Agreeableness | Neuroticism | Evidence Source |
|---|---|---|---|---|---|---|
| `alex.rivera` | 72 | 81 | 78 | 58 | 35 | `self_report` |
| `jordan.chen` | 65 | 88 | 52 | 71 | 42 | `self_report` |
| `sam.okafor` | 61 | 74 | 90 | 68 | 38 | `self_report` |
| `morgan.kim` | 79 | 77 | 41 | 65 | 55 | `self_report` |
| `casey.walsh` | 83 | 69 | 63 | 76 | 28 | `validated` |

**Conflict Style (five modes must sum to 100)**

| PersonID | Competing | Collaborating | Compromising | Avoiding | Accommodating | Evidence Source |
|---|---|---|---|---|---|---|
| `alex.rivera` | 35 | 30 | 20 | 5 | 10 | `observed` |
| `jordan.chen` | 15 | 45 | 25 | 10 | 5 | `observed` |
| `sam.okafor` | 40 | 25 | 20 | 5 | 10 | `observed` |
| `morgan.kim` | 10 | 35 | 25 | 25 | 5 | `self_report` |
| `casey.walsh` | 10 | 40 | 30 | 5 | 15 | `self_report` |

**Psychological Safety (items 1–7, scale 1..5)**

| PersonID | Item1 | Item2 | Item3 | Item4 | Item5 | Item6 | Item7 | Norm Score (computed) | Evidence Source |
|---|---|---|---|---|---|---|---|---|---|
| `alex.rivera` | 4 | 4 | 3 | 4 | 4 | 3 | 3 | 64 | `self_report` |
| `jordan.chen` | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 71 | `self_report` |
| `sam.okafor` | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 50 | `self_report` |
| `morgan.kim` | 2 | 3 | 2 | 2 | 3 | 2 | 3 | 36 | `self_report` |
| `casey.walsh` | 4 | 5 | 4 | 5 | 4 | 4 | 4 | 82 | `self_report` |

Norm score formula: `ROUND(100 * (AVERAGE(Item1:Item7) - 1) / 4, 0)`. Group aggregate (computed): 61.

**Communication & Decision Style (all 0..100 direct entry)**

| PersonID | Directness | Context Orientation | Verbal Dominance | Listening Quality | Feedback Tolerance | Analytical vs Intuitive | Risk Appetite | Decision Speed | Ambiguity Tolerance | Evidence Source |
|---|---|---|---|---|---|---|---|---|---|---|
| `alex.rivera` | 85 | 35 | 78 | 55 | 62 | 55 | 68 | 80 | 60 | `observed` |
| `jordan.chen` | 72 | 42 | 45 | 78 | 71 | 85 | 42 | 58 | 45 | `observed` |
| `sam.okafor` | 90 | 28 | 88 | 51 | 58 | 35 | 78 | 88 | 72 | `observed` |
| `morgan.kim` | 52 | 55 | 30 | 82 | 68 | 88 | 38 | 42 | 52 | `self_report` |
| `casey.walsh` | 65 | 68 | 55 | 88 | 80 | 62 | 50 | 62 | 75 | `observed` |

**Emotional Intelligence (all 0..100)**

| PersonID | Perceiving | Using | Understanding | Managing | Evidence Source |
|---|---|---|---|---|---|
| `alex.rivera` | 68 | 70 | 65 | 72 | `self_report` |
| `jordan.chen` | 75 | 68 | 78 | 72 | `self_report` |
| `sam.okafor` | 62 | 72 | 55 | 58 | `self_report` |
| `morgan.kim` | 78 | 55 | 72 | 60 | `self_report` |
| `casey.walsh` | 82 | 78 | 80 | 85 | `validated` |

**Attachment Tendencies (optional; all four must sum to 100 when present)**

| PersonID | Secure | Anxious | Avoidant | Fearful | Evidence Source |
|---|---|---|---|---|---|
| `alex.rivera` | 55 | 20 | 15 | 10 | `inferred` |
| `jordan.chen` | 65 | 18 | 12 | 5 | `inferred` |
| `sam.okafor` | 45 | 30 | 15 | 10 | `inferred` |
| `morgan.kim` | 40 | 35 | 15 | 10 | `inferred` |
| `casey.walsh` | 70 | 15 | 10 | 5 | `inferred` |

---

#### Gate A — Sub-tasks

##### A.0 — Platform Decision + Workbook Skeleton
- [ ] Confirm platform: Google Sheets (recommended) or Excel — log decision in Decisions Log below.
- [ ] Create new workbook; name it `group-dynamics-simulator-phase1`.
- [ ] Create tab stubs in this order: `README-Consent`, `People`, `Big Five`, `Conflict Style`, `Psychological Safety`, `Comm-Decision Style`, `EQ`, `Attachment`, `Gate-A-Validation-Log`.
- [ ] Add a **Metadata** named cell or header row in `README-Consent` with: `sheet_version = phase1_gateA_v1`, `created_date`, `platform`.
- [ ] Protect formula cells from accidental edits where the platform supports it.

**DoD**: Workbook exists with 9 correctly named tabs; metadata cell present; platform decision logged.

##### A.1 — README/Consent Tab
- [ ] Section 1 — Project description (2–3 sentences, personal use, non-clinical).
- [ ] Section 2 — Ethical use reminder: not for hiring, legal, clinical, or multi-tenant use.
- [ ] Section 3 — Consent note: assessments used with knowledge of subjects or are self-reports.
- [ ] Section 4 — Evidence source legend: `validated`, `self_report`, `observed`, `inferred`, `missing` with plain-language definitions.
- [ ] Section 5 — Tab navigation guide: what each tab does, in order.
- [ ] Section 6 — Version and session log table (columns: date, editor, change description).

**DoD**: README tab readable in isolation; someone unfamiliar with the project can understand purpose, ethical limits, and tab structure without reading other files.

##### A.2 — People Tab
- [ ] Header row: `PersonID | DisplayName | Role | GroupMembership | AuthorityLevel | IsActive`.
- [ ] Column B (`PersonID`): data validation — custom formula or note enforcing slug pattern `^[a-z0-9._-]{3,64}$`. Add a helper column `ID_valid` = TRUE/FALSE using a REGEXMATCH (Sheets) or equivalent formula.
- [ ] Column C (`Role`): dropdown list — `leader, manager, ic, advisor, observer, other`.
- [ ] Column E (`AuthorityLevel`): integer, between 1 and 5 (data validation: whole number, 1–5).
- [ ] Column F (`IsActive`): dropdown — `TRUE, FALSE`.
- [ ] Named range `PersonIDs` pointing to all non-empty PersonID cells (B2:B[N]).
- [ ] Conditional formatting: highlight any row in red where `ID_valid = FALSE` or required fields are blank.
- [ ] Enter the 5-person synthetic team from the specification above.

**DoD**: 5-person roster entered; ID_valid = TRUE for all rows; Role, AuthorityLevel, IsActive all pass validation; named range `PersonIDs` resolves correctly.

##### A.3 — Big Five Tab
- [ ] Layout: one row per person; PersonID pulled via `=IFERROR(People.B2, "")` or equivalent VLOOKUP/IMPORTRANGE pattern so names stay in sync automatically.
- [ ] Input columns: `O_raw | C_raw | E_raw | A_raw | N_raw` (integer 0..100 per cell).
- [ ] Data validation per input cell: whole number, 0–100.
- [ ] Phase 1 note: raw inputs ARE the normalized 0..100 scores (direct entry); no additional formula needed. Label columns accordingly: `Openness (0-100)`, etc.
- [ ] Evidence source column: dropdown — `validated, self_report, observed, inferred, missing`.
- [ ] Missing-data flag column: `IF(COUNTA(O_raw:N_raw)<5, TRUE, FALSE)`.
- [ ] Conditional formatting: red cell for any value outside 0–100.
- [ ] Enter the Big Five synthetic data.

**DoD**: All 5 persons' OCEAN data entered; no out-of-range values; evidence source set per row; missing-data flag = FALSE for all rows.

##### A.4 — Conflict Style Tab
- [ ] Layout: one row per person; PersonID auto-populated from People tab.
- [ ] Input columns: `Competing | Collaborating | Compromising | Avoiding | Accommodating` (integer 0..100 each).
- [ ] Data validation per cell: whole number, 0–100.
- [ ] Computed column `Mode_Sum` = `SUM(Competing:Accommodating)`.
- [ ] Computed column `Sum_Valid` = `IF(ABS(Mode_Sum - 100) <= 1, TRUE, FALSE)`.
- [ ] Conditional formatting: red row highlight when `Sum_Valid = FALSE`.
- [ ] Evidence source dropdown column.
- [ ] Optional proportional-normalization output columns: `Competing_pct = ROUND(100*Competing/Mode_Sum, 0)` etc. — only activate when `Sum_Valid = FALSE` to auto-rescale; otherwise display raw values.
- [ ] Enter the Conflict Style synthetic data.

**DoD**: All 5 rows entered; Mode_Sum ∈ [99,101] for all rows; Sum_Valid = TRUE for all rows; no validation errors.

##### A.5 — Psychological Safety Tab
- [ ] Layout: one row per person; PersonID auto-populated.
- [ ] Input columns: `Item1 | Item2 | Item3 | Item4 | Item5 | Item6 | Item7` (integer 1..5 each).
- [ ] Data validation: whole number, 1–5.
- [ ] Computed column `Person_PS_Score = ROUND(100 * (AVERAGE(Item1:Item7) - 1) / 4, 0)`.
- [ ] Computed cell `Group_PS_Aggregate = ROUND(AVERAGE(all Person_PS_Score cells), 0)` (label clearly; placed below the person rows or in a summary section).
- [ ] Missing-data flag: `IF(COUNTA(Item1:Item7)<7, TRUE, FALSE)`.
- [ ] Evidence source dropdown.
- [ ] Enter the Psych Safety synthetic data.

**DoD**: All 5 rows entered; per-person scores match the specification above (±1 rounding tolerance); Group_PS_Aggregate = 61 (±1); missing-data flag = FALSE for all rows.

##### A.6 — Communication & Decision Style Tab
- [ ] Layout: one row per person; PersonID auto-populated.
- [ ] Communication input columns (5): `Directness | Context Orientation | Verbal Dominance | Listening Quality | Feedback Tolerance` (integer 0..100).
- [ ] Decision input columns (4): `Analytical vs Intuitive | Risk Appetite | Decision Speed | Ambiguity Tolerance` (integer 0..100).
- [ ] Data validation per cell: whole number, 0–100.
- [ ] Column annotations: add a comment or label row below headers clarifying polarity where non-obvious (e.g., `Context Orientation: 0=low-context, 100=high-context`; `Analytical vs Intuitive: 0=intuitive, 100=analytical`).
- [ ] Evidence source dropdown.
- [ ] Missing-data flag: TRUE if ≥5 of 9 fields are blank for a person.
- [ ] Enter the Comm/Decision synthetic data.

**DoD**: All 5 rows filled; no out-of-range values; polarity labels present; missing-data flag = FALSE for all rows.

##### A.7 — EQ Tab
- [ ] Layout: one row per person; PersonID auto-populated.
- [ ] Input columns: `Perceiving | Using | Understanding | Managing` (integer 0..100).
- [ ] Data validation: whole number, 0–100.
- [ ] Computed column `EQ_Composite = ROUND(AVERAGE(Perceiving:Managing), 0)` (with missing-data guard).
- [ ] Missing-data flag: TRUE if any of the 4 fields is blank.
- [ ] Evidence source dropdown.
- [ ] Enter the EQ synthetic data.

**DoD**: All 5 rows filled; EQ_Composite calculated correctly; no out-of-range values; missing-data flag = FALSE for all rows.

##### A.8 — Attachment Tendencies Tab
- [ ] Layout: one row per person; PersonID auto-populated.
- [ ] Input columns: `Secure | Anxious | Avoidant | Fearful` (integer 0..100 each).
- [ ] Data validation: whole number, 0–100.
- [ ] Computed column `Attach_Sum = SUM(Secure:Fearful)`.
- [ ] Computed column `Sum_Valid = IF(COUNTA(Secure:Fearful)<4, "incomplete", IF(ABS(Attach_Sum-100)<=1, TRUE, FALSE))`.
- [ ] Conditional formatting: yellow row when `Sum_Valid = "incomplete"`; red row when `Sum_Valid = FALSE`.
- [ ] Evidence source dropdown.
- [ ] Note in tab header: "Attachment is optional in Phase 1. Leave all four blank if not used."
- [ ] Enter the Attachment synthetic data.

**DoD**: All 5 rows filled; Attach_Sum = 100 for all rows; Sum_Valid = TRUE for all rows.

##### A.9 — Gate A Validation Log Tab
- [ ] Create a table with columns: `Check ID | Tab | Check Description | Expected | Actual | Pass/Fail | Notes | Date | Reviewer`.
- [ ] Populate with the following required checks (one row per check):

| Check ID | Tab | Check Description |
|---|---|---|
| GA-01 | People | All 5 PersonIDs match slug pattern |
| GA-02 | People | No duplicate PersonIDs |
| GA-03 | People | Role values all in allowed enum |
| GA-04 | People | AuthorityLevel all in 1..5 |
| GA-05 | Big Five | All OCEAN values in 0..100 |
| GA-06 | Big Five | No missing-data flags |
| GA-07 | Conflict | Mode sums all within 99–101 |
| GA-08 | Conflict | Sum_Valid = TRUE for all 5 rows |
| GA-09 | Psych Safety | All item values in 1..5 |
| GA-10 | Psych Safety | Per-person scores match spec (±1) |
| GA-11 | Psych Safety | Group aggregate = 61 (±1) |
| GA-12 | Comm/Decision | All values in 0..100 |
| GA-13 | Comm/Decision | Polarity labels present |
| GA-14 | EQ | All values in 0..100; composites computed |
| GA-15 | Attachment | Attach_Sum = 100 for all 5 rows |
| GA-16 | Cross-tab | PersonID in each assessment tab resolves to a valid People.PersonID |
| GA-17 | Workbook | Sheet version tag = `phase1_gateA_v1` present |

- [ ] Mark all checks Pass/Fail after data entry.
- [ ] Resolve all Fail checks before claiming Gate A complete.

**DoD**: All 17 checks marked Pass; no open Fail rows; reviewer name and date filled in.

---

#### Gate A — Definition of Done Checklist

Use this checklist to confirm Gate A is complete before beginning Gate B.

- [ ] **A.DoD.1** — People tab supports stable IDs, role metadata, active flags, and cross-tab lookup references (named range `PersonIDs` resolves).
- [ ] **A.DoD.2** — Big Five, Conflict Style, Psychological Safety, Communication/Decision, EQ, and optional Attachment tabs are implemented with input constraints from the Phase 1 contract (bounds, sum rules, enums).
- [ ] **A.DoD.3** — Validation catches required fields, range violations, and profile sum checks (Conflict and Attachment) with clear Pass/Fail indicators visible without formula inspection.
- [ ] **A.DoD.4** — Normalized/computed per-person outputs (psych safety score, conflict sums, EQ composite) calculate correctly for the full 5-person synthetic dataset without manual intervention.
- [ ] **A.DoD.5** — No unresolved validation errors remain in the workbook (Gate A Validation Log shows all 17 checks = Pass).
- [ ] **Artifact: Sheet version tag** `phase1_gateA_v1` present in workbook metadata.
- [ ] **Artifact: Sample data snapshot** exported (CSV per tab or full XLSX) and filename/location recorded here: `[fill in path or link]`.
- [ ] **Artifact: Gate A Validation Log** filled in with date, reviewer, all checks Pass.

---

### Phase 1 Tasks

#### 1.1 — Design & Specification
- [x] Read and understand full system design document
- [x] Create CLAUDE.md session context file
- [x] Create PLAN.md implementation plan
- [x] Define exact field lists and validation rules for each tab — locked in Phase 1 contract Field Dictionary
- [x] Define the normalized score computation rules — locked in Phase 1 contract Scoring Spec
- [x] Define the confidence rating system — categorical (validated/self_report/observed/inferred/missing), locked in contract

#### 1.2 — Spreadsheet Build: People and Roles
- [x] Create People tab with columns: PersonID, DisplayName, Role, GroupMembership, AuthorityLevel, IsActive — `scripts/build_workbook.py`
- [x] Create named range `PersonIDs` for PersonID cross-referencing in other tabs — `scripts/build_workbook.py`
- [x] Add README/Consent tab with instructions and ethical notes — `scripts/build_workbook.py`

#### 1.3 — Spreadsheet Build: Assessment Tabs
- [x] **Big Five tab**: OCEAN 0–100 direct entry, evidence source dropdown, missing-data flag — `scripts/build_workbook.py`
- [x] **Conflict Style tab**: Five-mode profile, Mode_Sum formula, Sum_Valid check (100±1), evidence source — `scripts/build_workbook.py`
- [x] **Psychological Safety tab**: 7-item Edmondson survey, per-person PS score, group aggregate, evidence source — `scripts/build_workbook.py`
- [x] **Communication & Decision Style tab**: 9 fields (5 comm + 4 decision), polarity labels, evidence source, missing-data flag — `scripts/build_workbook.py`
- [x] **Emotional Intelligence tab**: 4 dimensions, EQ_Composite formula, evidence source, missing-data flag — `scripts/build_workbook.py`
- [x] **Attachment Tendencies tab**: 4 tendencies, Attach_Sum + Sum_Valid, evidence source — `scripts/build_workbook.py`

#### 1.4 — Spreadsheet Build: Relationship Matrix
- [x] **Relationship Matrix tab**: Auto-populated person list from People tab. Directed pairwise fields: trust, influence, emotional closeness, respect, conflict intensity, dependency, communication frequency, avoidance, alliance/coalition, power differential. Evidence source per pair. Notes field. — `scripts/build_workbook.py`
- [x] Add formula to compute aggregate relationship health score per pair and overall network health — `scripts/build_workbook.py`

#### 1.5 — Spreadsheet Build: Group and Scenario
- [x] **Group Context tab**: Group type, formal/informal structure, shared goals, explicit/implicit norms, psychological safety aggregate, decision rules, conflict/cohesion history, current stress level, role clarity, cultural context, environmental constraints — `scripts/build_workbook.py`
- [x] **Scenario Builder tab**: Title, type, triggering event description, stakes level (1–5), emotional intensity (1–5), ambiguity level (1–5), time pressure (1–5), resource constraints, public visibility flag, required decision description, success criteria, failure consequences, known facts list, uncertain facts list, intervention options to test — `scripts/build_workbook.py`

#### 1.6 — Spreadsheet Build: Simulation Config
- [x] **Simulation Config tab**: Number of passes (1–10), randomness setting (Low/Medium/High), simulation depth (Surface/Standard/Deep), dialogue enabled (Y/N), report detail level (Summary/Standard/Full), intervention testing mode (Baseline/Compare), source evidence strictness (Strict/Moderate/Lenient), guardrail verbosity (Minimal/Standard/Verbose), and required prompt version key (`P<major>.<minor>`) — `scripts/build_workbook.py`

#### 1.7 — Spreadsheet Build: Profile Output & Prompt Generation
- [ ] **Structured Profile Output tab**: Computed summary view pulling from all assessment tabs. Formatted for human review. Shows: person name, role, OCEAN summary (high/medium/low per trait), dominant conflict mode, primary communication patterns, decision style summary, EQ summary, attachment tendency, key motivations/values/triggers. Confidence rating per section. Missing data flags.
- [ ] **Prompt Inputs tab**: Formula-generated prompt block. Assembles system prompt, person profile blocks, relationship data block, group context block, scenario block, config block, and output format instructions. Single cell with full concatenated prompt ready to copy-paste into Claude.

#### 1.8 — Spreadsheet Build: Output Logging
- [ ] **Simulation Output Log tab**: Table with columns: RunID, Date, ScenarioTitle, PromptVersionKey, PassNumber, RawOutput (paste area), OutcomeClassification, ProbabilityEstimate, ConfidenceEstimate, KeyFindings, Recommendations, LimitationNotes, ReviewedBy, EvidenceAnchoringScore (1–5), InternalConsistencyScore (1–5), PlausibilityScore (1–5), InterventionUsefulnessScore (1–5), UncertaintyQualityScore (1–5), RubricAverageScore, RubricNotes. Auto-generate RunID from timestamp.

#### 1.9 — Spreadsheet Build: Visuals
- [ ] **Visuals tab**: Relationship trust heat map (matrix visualization using conditional formatting), Influence map (sorted bar chart), OCEAN radar charts per person, Conflict style stacked bar per person, Outcome cluster distribution chart (manual input from simulation log)

#### 1.10 — Prompt Engineering
- [ ] Draft System Role prompt for the simulator agent
- [ ] Draft Person Profile block template (one block per person)
- [ ] Draft Relationship block template
- [ ] Draft Group Context block template
- [ ] Draft Scenario block template
- [ ] Draft Output Format instructions block (aligned with Simulation Output Object schema)
- [ ] Draft Evaluator prompt rubric with numeric scores (1–5) for evidence anchoring, internal consistency, plausibility, intervention usefulness, and uncertainty quality
- [ ] Test prompt with synthetic team data (3-person team, simple scenario)
- [ ] Test prompt with realistic team data (5–8 person team, complex scenario)
- [ ] Iterate until output structure is consistent and evidence-anchored
- [ ] Only promote prompt version when rubric average improves in at least 3 comparable scenarios

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

| RunID | Dataset Used | Scenario ID/Type | Prompt Version Key | Model/Version | Evidence Anchoring (1–5) | Internal Consistency (1–5) | Plausibility (1–5) | Intervention Usefulness (1–5) | Uncertainty Quality (1–5) | Rubric Avg | Key Outcome Quality Notes | Comparable Baseline? | Decision Taken |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

## Guardrail Exceptions

Record one row for each run with `run_status=failed_guardrail` to support prompt refinement.

| Date | RunID | Prompt Version Key | Failed Check(s) | Trigger Phrase / Missing Section | Action Taken | Prompt Refinement Note |
|---|---|---|---|---|---|---|
| _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

### End-of-Session Update Checklist (<= 5 minutes)

1. Add/complete Run Ledger rows for all trials finished this session.
2. Ensure each row includes prompt version key plus all five rubric dimension scores and rubric average.
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
| 2026-04-24 | Use Excel (.xlsx) as Phase 1 workbook format, built via Python/openpyxl (`scripts/build_workbook.py`) | Enables version-controlled, reproducible workbook generation; eliminates manual tab setup errors; easily importable into Google Sheets if sharing is needed later |
| 2026-04-24 | Pre-populate synthetic dataset directly in the build script | Guarantees all 17 Gate A validation checks have test data to run against from day one |

---

## Notes / Open Questions

- **Spreadsheet format**: ~~Open~~ **Resolved** — Excel (.xlsx) via `scripts/build_workbook.py`. Import into Google Sheets for sharing if needed.
- **Prompt format**: Should prompt blocks be JSON, YAML, or structured natural language? JSON is machine-parseable; natural language may produce better simulation quality. Hybrid likely best — natural language narrative wrapping JSON data blocks.
- **Evidence confidence scale**: Design doc mentions 1–5 numeric or categorical labels (Validated/Self-report/Observed/Inferred/Missing). Categorical is clearer for users; can map to numeric for computations.
- **OCEAN scoring**: Design doc recommends IPIP-based Big Five (50-item or 120-item). In Phase 1, allow manual score entry (pre-computed from any validated instrument) rather than administering the assessment in the spreadsheet.
- **Phase 2 stack confirmation**: Confirm Python/FastAPI vs. Node.js/Express before starting Phase 2. User preference matters here.
