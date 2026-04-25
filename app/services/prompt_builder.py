"""
Prompt assembly service.

Deterministically assembles the Phase 1 contract prompt format from canonical
persisted records. Emits transient prompt artifacts — never persisted as
first-class columns.

Prompt I/O spec (frozen Phase 1 contract v1):
  === SIMULATION_PROMPT_BEGIN ===
  version: phase1_contract_v1
  run_id: <id>
  prompt_version_key: <key>
  group_id: <id>
  scenario_id: <id>

  [CONFIG] ...
  [PEOPLE] ...
  [RELATIONSHIPS] ...
  [GROUP_CONTEXT] ...
  [SCENARIO] ...
  [OUTPUT_REQUIREMENTS] ...
  === SIMULATION_PROMPT_END ===
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.entities import (
    GroupContext, Scenario, SimulationConfig, SimulationRun,
    AssessmentSnapshot, RelationshipEdge, GroupMembership,
)

OUTPUT_REQUIREMENTS = """Return one JSON object that exactly matches the schema in this contract.
No markdown. No prose outside JSON.
Mandatory sections must be present in every run output:
1) confidence_statement
2) limitation_statement
3) non_determinism_disclaimer
4) evidence_inference_simulation_separation_check
If any mandatory section is missing, mark run_status="failed_guardrail".
If deterministic or diagnostic wording appears (e.g. "will", "proves", "correct intervention is"), mark run_status="failed_guardrail".

Output schema:
{
  "run_id": "string",
  "scenario_id": "string",
  "generated_at_utc": "ISO-8601 datetime",
  "outcome_clusters": [
    {"cluster_id": "string", "label": "string", "probability": 0.0, "narrative": "string",
     "key_drivers": [], "early_signals": [], "confidence": 0.0}
  ],
  "individual_forecasts": [
    {"person_id": "string", "likely_behaviors": [], "stress_response": "string",
     "influence_on_others": "string", "confidence": 0.0}
  ],
  "interventions": [
    {"intervention_id": "string", "description": "string",
     "target_level": "individual|dyad|group|leader",
     "expected_effect": "string", "risk": "string", "estimated_impact": 0.0}
  ],
  "evidence_coverage": {
    "missing_field_ids": [], "coverage_ratio": 0.0, "overall_confidence": 0.0
  },
  "confidence_statement": "string",
  "limitation_statement": "string",
  "non_determinism_disclaimer": "string",
  "evidence_inference_simulation_separation_check": {
    "evidence_only_claims": [], "inference_claims": [], "simulation_claims": [],
    "mixing_detected": false, "mixing_notes": []
  },
  "limitations": [],
  "run_status": "ok|failed_guardrail"
}"""


def _person_block(person, snapshot: Optional[AssessmentSnapshot]) -> dict:
    p = {
        "person.id": person.id,
        "person.display_name": person.display_name,
        "person.role": person.role,
        "person.group_membership": person.group_membership,
        "person.authority_level": person.authority_level,
        "person.is_active": person.is_active,
    }
    if snapshot:
        p.update({
            "person.ocean.openness": snapshot.big_five_openness,
            "person.ocean.conscientiousness": snapshot.big_five_conscientiousness,
            "person.ocean.extraversion": snapshot.big_five_extraversion,
            "person.ocean.agreeableness": snapshot.big_five_agreeableness,
            "person.ocean.neuroticism": snapshot.big_five_neuroticism,
            "person.conflict.competing": snapshot.conflict_competing,
            "person.conflict.collaborating": snapshot.conflict_collaborating,
            "person.conflict.compromising": snapshot.conflict_compromising,
            "person.conflict.avoiding": snapshot.conflict_avoiding,
            "person.conflict.accommodating": snapshot.conflict_accommodating,
            "person.psych_safety.item_1": snapshot.psych_safety_item_1,
            "person.psych_safety.item_2": snapshot.psych_safety_item_2,
            "person.psych_safety.item_3": snapshot.psych_safety_item_3,
            "person.psych_safety.item_4": snapshot.psych_safety_item_4,
            "person.psych_safety.item_5": snapshot.psych_safety_item_5,
            "person.psych_safety.item_6": snapshot.psych_safety_item_6,
            "person.psych_safety.item_7": snapshot.psych_safety_item_7,
            "person.comm.directness": snapshot.comm_directness,
            "person.comm.context_orientation": snapshot.comm_context_orientation,
            "person.comm.verbal_dominance": snapshot.comm_verbal_dominance,
            "person.comm.listening_quality": snapshot.comm_listening_quality,
            "person.comm.feedback_tolerance": snapshot.comm_feedback_tolerance,
            "person.decision.analytical_vs_intuitive": snapshot.decision_analytical_vs_intuitive,
            "person.decision.risk_appetite": snapshot.decision_risk_appetite,
            "person.decision.speed": snapshot.decision_speed,
            "person.decision.ambiguity_tolerance": snapshot.decision_ambiguity_tolerance,
            "person.eq.perceiving": snapshot.eq_perceiving,
            "person.eq.using": snapshot.eq_using,
            "person.eq.understanding": snapshot.eq_understanding,
            "person.eq.managing": snapshot.eq_managing,
            "person.attachment.secure": snapshot.attachment_secure,
            "person.attachment.anxious": snapshot.attachment_anxious,
            "person.attachment.avoidant": snapshot.attachment_avoidant,
            "person.attachment.fearful": snapshot.attachment_fearful,
            "evidence_source": snapshot.evidence_source,
            "missing_data_flag": snapshot.missing_data_flag,
        })
    return p


def _relationship_block(edge: RelationshipEdge) -> dict:
    return {
        "rel.from_person_id": edge.from_person_id,
        "rel.to_person_id": edge.to_person_id,
        "rel.trust": edge.trust,
        "rel.influence": edge.influence,
        "rel.emotional_closeness": edge.emotional_closeness,
        "rel.respect": edge.respect,
        "rel.conflict_intensity": edge.conflict_intensity,
        "rel.dependency": edge.dependency,
        "rel.communication_frequency": edge.communication_frequency,
        "rel.avoidance": edge.avoidance,
        "rel.alliance": edge.alliance,
        "rel.power_differential": edge.power_differential,
        "rel.evidence_source": edge.evidence_source,
        "rel.notes": edge.notes,
    }


def _group_block(group: GroupContext) -> dict:
    return {
        "group.id": group.id,
        "group.type": group.type,
        "group.structure": group.structure,
        "group.shared_goals": group.shared_goals,
        "group.norms.explicit": group.norms_explicit,
        "group.norms.implicit": group.norms_implicit,
        "group.decision_rules": group.decision_rules,
        "group.conflict_history": group.conflict_history,
        "group.stress_level": group.stress_level,
        "group.role_clarity": group.role_clarity,
        "group.cultural_context": group.cultural_context,
        "group.environmental_constraints": group.environmental_constraints,
    }


def _scenario_block(scenario: Scenario) -> dict:
    return {
        "scenario.id": scenario.id,
        "scenario.title": scenario.title,
        "scenario.type": scenario.type,
        "scenario.trigger_event": scenario.trigger_event,
        "scenario.stakes_level": scenario.stakes_level,
        "scenario.emotional_intensity": scenario.emotional_intensity,
        "scenario.ambiguity_level": scenario.ambiguity_level,
        "scenario.time_pressure": scenario.time_pressure,
        "scenario.resource_constraints": scenario.resource_constraints,
        "scenario.public_visibility": scenario.public_visibility,
        "scenario.required_decision": scenario.required_decision,
        "scenario.success_criteria": scenario.success_criteria,
        "scenario.failure_consequences": scenario.failure_consequences,
        "scenario.known_facts": scenario.known_facts or [],
        "scenario.uncertain_facts": scenario.uncertain_facts or [],
        "scenario.intervention_options": scenario.intervention_options or [],
    }


def _config_block(config: SimulationConfig) -> dict:
    return {
        "sim.prompt_version_key": config.prompt_version_key,
        "sim.passes": config.passes,
        "sim.randomness": config.randomness,
        "sim.depth": config.depth,
        "sim.dialogue_enabled": config.dialogue_enabled,
        "sim.report_detail_level": config.report_detail_level,
        "sim.intervention_mode": config.intervention_mode,
        "sim.evidence_strictness": config.evidence_strictness,
        "sim.guardrail_verbosity": config.guardrail_verbosity,
    }


def build_prompt(db: Session, run: SimulationRun) -> str:
    """Assemble the full simulation prompt from canonical records."""
    group: GroupContext = db.get(GroupContext, run.group_id)
    scenario: Scenario = db.get(Scenario, run.scenario_id)
    config: SimulationConfig = db.get(SimulationConfig, run.simulation_config_id)

    # Collect members in deterministic order (sort by person_id)
    memberships = (
        db.query(GroupMembership)
        .filter(GroupMembership.group_id == run.group_id)
        .order_by(GroupMembership.person_id)
        .all()
    )

    people_blocks = []
    for m in memberships:
        person = m.person
        # Most recent snapshot per person
        snapshot = (
            db.query(AssessmentSnapshot)
            .filter(AssessmentSnapshot.person_id == person.id)
            .order_by(AssessmentSnapshot.snapshot_date.desc())
            .first()
        )
        people_blocks.append(_person_block(person, snapshot))

    # Relationships between group members — deterministic sort
    member_ids = sorted(m.person_id for m in memberships)
    edges = (
        db.query(RelationshipEdge)
        .filter(
            RelationshipEdge.from_person_id.in_(member_ids),
            RelationshipEdge.to_person_id.in_(member_ids),
        )
        .order_by(RelationshipEdge.from_person_id, RelationshipEdge.to_person_id)
        .all()
    )
    rel_blocks = [_relationship_block(e) for e in edges]

    parts = [
        "=== SIMULATION_PROMPT_BEGIN ===",
        f"version: phase1_contract_v1",
        f"run_id: {run.id}",
        f"prompt_version_key: {config.prompt_version_key}",
        f"group_id: {run.group_id}",
        f"scenario_id: {run.scenario_id}",
        "",
        "[CONFIG]",
        json.dumps(_config_block(config), indent=2),
        "",
        "[PEOPLE]",
        json.dumps(people_blocks, indent=2),
        "",
        "[RELATIONSHIPS]",
        json.dumps(rel_blocks, indent=2),
        "",
        "[GROUP_CONTEXT]",
        json.dumps(_group_block(group), indent=2),
        "",
        "[SCENARIO]",
        json.dumps(_scenario_block(scenario), indent=2),
        "",
        "[OUTPUT_REQUIREMENTS]",
        OUTPUT_REQUIREMENTS,
        "=== SIMULATION_PROMPT_END ===",
    ]
    return "\n".join(parts)


def hash_prompt(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode()).hexdigest()[:16]


def generate_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    import random, string
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"run-{ts}-{suffix}"
