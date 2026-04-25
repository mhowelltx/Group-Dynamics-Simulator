#!/usr/bin/env python3
"""
Phase 1.10 prompt trial runner.

Generates two prompt payloads using the current Phase 1 workbook synthetic data:
1) A synthetic 3-person simple scenario trial.
2) A realistic 5-person complex scenario trial.

Also performs a deterministic structure check by hashing three consecutive exports
for each trial profile and writing a compact report artifact.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from build_workbook import PEOPLE, GROUP_CONTEXT, SCENARIO_CONTEXT


SYSTEM_ROLE = (
    "You are an organizational group dynamics simulator for coaching/research reflection "
    "(not diagnosis, hiring, legal, or disciplinary use). Maintain explicit separation of "
    "EVIDENCE, INFERENCE, and SIMULATION layers. Use cautious probabilistic language and "
    "uncertainty statements. Reject deterministic claims and avoid pathologizing labels."
)
PERSON_PROFILES = (
    "For each person_id from Structured Profile Output, create a compact block: role, OCEAN "
    "low/medium/high summary, dominant conflict mode, communication and decision pattern, EQ "
    "composite summary, attachment tendency (or missing), confidence category, and missing-data "
    "flags. For each non-trivial claim, reference which input column(s) support it."
)
RELATIONSHIP_DATA = (
    "Use directed pair edges from Relationship Matrix: trust, influence, emotional_closeness, "
    "respect, conflict_intensity, dependency, communication_frequency, avoidance, alliance, "
    "power_differential, plus computed health score. Highlight asymmetries, high-conflict dyads, "
    "and likely coalition fault lines."
)
GROUP_CONTEXT_TEXT = (
    "Use Group Context fields exactly as listed (type, structure, goals, norms, decision rules, "
    "conflict history, stress level, role clarity, cultural context, constraints). Treat these as "
    "system-level boundary conditions for behavior interpretation."
)
SIMULATION_PROCEDURE = (
    "Run N passes. For each pass output steps: (1) private appraisal by each actor, (2) first "
    "public move, (3) interaction sequence and influence shifts, (4) conflict escalation/"
    "de-escalation markers, (5) decision or non-decision point, (6) short-term outcome "
    "classification, (7) evidence-consistency check with uncertainties."
)
OUTPUT_REQUIREMENTS = (
    "Return markdown sections: Executive Summary; Scenario and Data Inputs; Behavior Trace by pass; "
    "Outcome Clusters with probabilities; Individual Behavior Forecasts; Intervention Options "
    "(baseline vs compare if enabled); Limitations & Ethics. Must include: confidence statement, "
    "limitations statement, non-determinism disclaimer, and explicit evidence-vs-inference-vs-"
    "simulation separation check."
)
OUTPUT_FORMAT_CONTRACT = (
    "Also emit a JSON object with keys: run_id, prompt_version_key, scenario_title, outcome_clusters[], "
    "individual_forecasts[], intervention_recommendations[], confidence_statement, "
    "limitation_statement, layer_separation_check, and rubric_self_check."
)
EVALUATOR_RUBRIC = (
    "After simulation output, score 1-5 with short rationale for: evidence anchoring, internal "
    "consistency, plausibility, intervention usefulness, and uncertainty quality. Compute "
    "rubric_average_score (2 decimals). Scoring anchors: 1=poor/missing, 3=adequate/mixed, "
    "5=strong/explicit and traceable."
)


@dataclass(frozen=True)
class TrialCase:
    trial_id: str
    prompt_version_key: str
    run_id: str
    people: list[dict]
    scenario_title: str
    scenario_type: str
    scenario_text: str
    sim_config: dict[str, str]


def _render_people_block(people: list[dict]) -> str:
    return "\n".join(
        f"- person_id={p['id']} | display_name={p['name']} | role={p['role']} | authority={p['authority']}"
        for p in people
    )


def _render_group_context() -> str:
    keys = [
        "group.id",
        "group.type",
        "group.structure",
        "group.shared_goals",
        "group.norms.explicit",
        "group.norms.implicit",
        "group.decision_rules",
        "group.conflict_history",
        "group.stress_level",
        "group.role_clarity",
        "group.cultural_context",
        "group.environmental_constraints",
    ]
    return "\n".join(f"- {k}: {GROUP_CONTEXT[k]}" for k in keys)


def _render_prompt(case: TrialCase) -> str:
    scenario_block = (
        f"- scenario.title: {case.scenario_title}\n"
        f"- scenario.type: {case.scenario_type}\n"
        f"- scenario.trigger_event: {case.scenario_text}"
    )
    sim_config_block = "\n".join(f"- {k}: {v}" for k, v in case.sim_config.items())

    sections = [
        ("SYSTEM ROLE", SYSTEM_ROLE),
        ("PERSON PROFILES", f"{PERSON_PROFILES}\n\n{_render_people_block(case.people)}"),
        ("RELATIONSHIP DATA", RELATIONSHIP_DATA),
        ("GROUP CONTEXT", f"{GROUP_CONTEXT_TEXT}\n\n{_render_group_context()}"),
        ("SCENARIO", scenario_block),
        ("SIMULATION CONFIG", sim_config_block),
        ("SIMULATION PROCEDURE", SIMULATION_PROCEDURE),
        ("OUTPUT REQUIREMENTS", OUTPUT_REQUIREMENTS),
        ("OUTPUT FORMAT CONTRACT", OUTPUT_FORMAT_CONTRACT),
        ("EVALUATOR RUBRIC PROMPT", EVALUATOR_RUBRIC),
        ("PROMPT_VERSION_KEY", case.prompt_version_key),
        ("RUN_ID", case.run_id),
    ]
    return "\n\n".join(f"{title}:\n{body}" for title, body in sections)


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _trial_cases() -> list[TrialCase]:
    return [
        TrialCase(
            trial_id="synthetic-3-person-simple",
            prompt_version_key="P1.1",
            run_id="phase1-trial-3p-simple",
            people=PEOPLE[:3],
            scenario_title="Weekly planning conflict over release priority",
            scenario_type="conflict",
            scenario_text=(
                "Two managers disagree on sprint allocation during a weekly planning meeting with "
                "moderate stakes and low external visibility."
            ),
            sim_config={
                "sim.passes": "2",
                "sim.randomness": "low",
                "sim.depth": "standard",
                "sim.dialogue_enabled": "true",
                "sim.report_detail_level": "standard",
                "sim.intervention_mode": "baseline",
                "sim.evidence_strictness": "strict",
                "sim.guardrail_verbosity": "standard",
            },
        ),
        TrialCase(
            trial_id="realistic-5-person-complex",
            prompt_version_key="P1.1",
            run_id="phase1-trial-5p-complex",
            people=PEOPLE,
            scenario_title=SCENARIO_CONTEXT["scenario.title"],
            scenario_type=SCENARIO_CONTEXT["scenario.type"],
            scenario_text=SCENARIO_CONTEXT["scenario.trigger_event"],
            sim_config={
                "sim.passes": "3",
                "sim.randomness": "medium",
                "sim.depth": "deep",
                "sim.dialogue_enabled": "true",
                "sim.report_detail_level": "full",
                "sim.intervention_mode": "compare",
                "sim.evidence_strictness": "strict",
                "sim.guardrail_verbosity": "verbose",
            },
        ),
    ]


def main() -> None:
    out_dir = Path("artifacts/prompt_trials")
    out_dir.mkdir(parents=True, exist_ok=True)

    report_rows = []
    for case in _trial_cases():
        prompts = [_render_prompt(case) for _ in range(3)]
        hashes = [_hash_prompt(p) for p in prompts]
        deterministic = len(set(hashes)) == 1

        prompt_path = out_dir / f"{case.trial_id}.md"
        prompt_path.write_text(prompts[0], encoding="utf-8")

        report_rows.append(
            {
                "trial_id": case.trial_id,
                "prompt_path": str(prompt_path),
                "deterministic_structure": deterministic,
                "hashes": hashes,
            }
        )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "results": report_rows,
    }
    json_path = out_dir / "determinism_report.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Wrote prompt trial artifacts to: {out_dir}")
    print(f"Wrote determinism report: {json_path}")


if __name__ == "__main__":
    main()
