"""Utilities to seed deterministic manual-testing data."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.entities import (
    AssessmentSnapshot,
    GroupContext,
    GroupMembership,
    Person,
    RelationshipEdge,
    Scenario,
    SimulationConfig,
    SimulationPass,
    SimulationRun,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def should_seed_test_data() -> bool:
    """True when deployment requested test-data bootstrap on startup."""
    return _as_bool(os.getenv("SEED_TEST_DATA"))


def seed_test_data(db: Session) -> dict[str, int]:
    """Seed a deterministic sample dataset for manual UI/API testing.

    Idempotent behavior: if the anchor group already exists, no inserts occur.
    """
    anchor_group_id = "manual-test-team"
    if db.get(GroupContext, anchor_group_id):
        return {"inserted": 0, "skipped": 1}

    people = [
        Person(id="alex.chen", display_name="Alex Chen", role="leader", group_membership="manual-test-team", authority_level=5),
        Person(id="maria.lopez", display_name="Maria Lopez", role="manager", group_membership="manual-test-team", authority_level=4),
        Person(id="jordan.kim", display_name="Jordan Kim", role="ic", group_membership="manual-test-team", authority_level=3),
        Person(id="sam.patel", display_name="Sam Patel", role="advisor", group_membership="manual-test-team", authority_level=2),
    ]

    db.add_all(people)

    group = GroupContext(
        id=anchor_group_id,
        type="team",
        structure="hybrid",
        shared_goals="Launch v2 planning cycle while reducing coordination overhead.",
        norms_explicit="Weekly demos, written decisions, and direct feedback in retros.",
        norms_implicit="Strong ownership culture with occasional escalation delays.",
        decision_rules="Consensus preferred; leader breaks ties under deadline pressure.",
        conflict_history="Past friction between product priorities and engineering timelines.",
        stress_level=4,
        role_clarity=68,
        cultural_context="Cross-functional remote team in North America.",
        environmental_constraints="Budget cap and eight-week delivery target.",
    )
    db.add(group)

    memberships = [
        GroupMembership(group_id=anchor_group_id, person_id="alex.chen"),
        GroupMembership(group_id=anchor_group_id, person_id="maria.lopez"),
        GroupMembership(group_id=anchor_group_id, person_id="jordan.kim"),
        GroupMembership(group_id=anchor_group_id, person_id="sam.patel"),
    ]
    db.add_all(memberships)

    assessments = [
        AssessmentSnapshot(
            person_id="alex.chen",
            evidence_source="validated",
            big_five_openness=72,
            big_five_conscientiousness=84,
            big_five_extraversion=63,
            big_five_agreeableness=58,
            big_five_neuroticism=29,
            conflict_competing=22,
            conflict_collaborating=28,
            conflict_compromising=20,
            conflict_avoiding=14,
            conflict_accommodating=16,
            attachment_secure=52,
            attachment_anxious=18,
            attachment_avoidant=20,
            attachment_fearful=10,
            psych_safety_item_1=4,
            psych_safety_item_2=4,
            psych_safety_item_3=3,
            psych_safety_item_4=4,
            psych_safety_item_5=4,
            psych_safety_item_6=3,
            psych_safety_item_7=4,
        ),
        AssessmentSnapshot(
            person_id="maria.lopez",
            evidence_source="self_report",
            big_five_openness=67,
            big_five_conscientiousness=76,
            big_five_extraversion=71,
            big_five_agreeableness=64,
            big_five_neuroticism=42,
            conflict_competing=15,
            conflict_collaborating=35,
            conflict_compromising=23,
            conflict_avoiding=12,
            conflict_accommodating=15,
            attachment_secure=46,
            attachment_anxious=24,
            attachment_avoidant=18,
            attachment_fearful=12,
            psych_safety_item_1=3,
            psych_safety_item_2=4,
            psych_safety_item_3=4,
            psych_safety_item_4=3,
            psych_safety_item_5=4,
            psych_safety_item_6=4,
            psych_safety_item_7=3,
        ),
    ]
    db.add_all(assessments)

    relationships = [
        RelationshipEdge(
            from_person_id="alex.chen",
            to_person_id="maria.lopez",
            trust=74,
            influence=81,
            emotional_closeness=56,
            respect=79,
            conflict_intensity=31,
            dependency=62,
            communication_frequency=87,
            avoidance=14,
            alliance=72,
            power_differential=45,
            evidence_source="observed",
        ),
        RelationshipEdge(
            from_person_id="maria.lopez",
            to_person_id="alex.chen",
            trust=69,
            influence=76,
            emotional_closeness=58,
            respect=73,
            conflict_intensity=36,
            dependency=57,
            communication_frequency=83,
            avoidance=17,
            alliance=68,
            power_differential=42,
            evidence_source="observed",
        ),
    ]
    db.add_all(relationships)

    scenario = Scenario(
        id="manual-test-crisis-01",
        title="Critical release quality incident",
        type="crisis",
        trigger_event="A high-visibility customer reports data inconsistencies after a release.",
        stakes_level=5,
        emotional_intensity=4,
        ambiguity_level=3,
        time_pressure=5,
        resource_constraints="Two engineers are on planned leave this week.",
        public_visibility=True,
        required_decision="Choose rollback vs. hotfix path and communication owner.",
        success_criteria="Contain incident within 24 hours and preserve executive trust.",
        failure_consequences="Escalation to board-level review and delayed launch roadmap.",
        known_facts=["Issue reproduced in two enterprise tenants", "Monitoring alarms started 09:12 UTC"],
        uncertain_facts=["Root cause may involve feature flag mismatch"],
        intervention_options=["Rollback", "Targeted hotfix", "Split-path response team"],
        group_id=anchor_group_id,
    )
    db.add(scenario)

    config = SimulationConfig(
        prompt_version_key="P2.1",
        passes=3,
        randomness="medium",
        depth="standard",
        dialogue_enabled=True,
        report_detail_level="standard",
        intervention_mode="compare",
        evidence_strictness="moderate",
        guardrail_verbosity="standard",
    )
    db.add(config)
    db.flush()

    run = SimulationRun(
        id="manual-test-run-001",
        group_id=anchor_group_id,
        scenario_id=scenario.id,
        simulation_config_id=config.id,
        generated_at_utc=_utcnow(),
        status="complete",
        prompt_hash="seeded-manual-test-hash",
        eval_evidence_anchoring_score=78,
        eval_internal_consistency_score=82,
        eval_plausibility_score=80,
        eval_intervention_usefulness_score=76,
        eval_uncertainty_quality_score=84,
        eval_rubric_notes="Seeded run for manual verification of list/detail/report screens.",
    )
    db.add(run)
    db.flush()

    db.add(
        SimulationPass(
            run_id=run.id,
            pass_index=1,
            output_json={
                "summary": "Team converges on a split-path response with Alex owning executive comms.",
                "confidence": "moderate",
            },
            missing_field_ids=[],
            coverage_ratio=0.92,
            overall_confidence=0.78,
        )
    )

    db.commit()
    return {"inserted": 1, "skipped": 0}
