"""Utilities to seed deterministic manual-testing data."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

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

SEED_FILE = Path(__file__).resolve().parent / "seed_data" / "manual_test_team.json"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def should_seed_test_data() -> bool:
    """True when deployment requested test-data bootstrap on startup."""
    return _as_bool(os.getenv("SEED_TEST_DATA"))


def _load_seed_payload() -> dict:
    with SEED_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _upsert_snapshot(db: Session, payload: dict) -> int:
    existing = db.query(AssessmentSnapshot).filter(AssessmentSnapshot.person_id == payload["person_id"]).first()
    if not existing:
        db.add(AssessmentSnapshot(**payload))
        return 1
    for field, value in payload.items():
        if field == "person_id":
            continue
        setattr(existing, field, value)
    return 0


def _upsert_relationship(db: Session, payload: dict) -> int:
    existing = (
        db.query(RelationshipEdge)
        .filter(
            RelationshipEdge.from_person_id == payload["from_person_id"],
            RelationshipEdge.to_person_id == payload["to_person_id"],
        )
        .first()
    )
    if not existing:
        db.add(RelationshipEdge(**payload))
        return 1
    for field, value in payload.items():
        setattr(existing, field, value)
    return 0


def seed_test_data(db: Session) -> dict[str, int]:
    """Seed deterministic manual-test data from a fixture payload.

    Idempotent behavior:
    - first run inserts full anchor dataset,
    - later runs upsert missing/incomplete snapshots + relationships.
    """
    payload = _load_seed_payload()
    group_payload = payload["group"]
    people_payload = payload["people"]
    memberships_payload = payload["memberships"]
    assessments_payload = payload["assessments"]
    relationships_payload = payload["relationships"]
    scenario_payload = payload["scenario"]
    config_payload = payload["config"]
    run_payload = payload["run"]
    pass_payload = payload["pass"]

    anchor_group_id = group_payload["id"]
    inserted = 0

    # Existing deployment path: upsert data for happy-path simulation coverage.
    if db.get(GroupContext, anchor_group_id):
        for p in people_payload:
            existing = db.get(Person, p["id"])
            if existing:
                for field, value in p.items():
                    setattr(existing, field, value)
            else:
                db.add(Person(**p))
                inserted += 1

        for m in memberships_payload:
            existing_membership = (
                db.query(GroupMembership)
                .filter(GroupMembership.group_id == m["group_id"], GroupMembership.person_id == m["person_id"])
                .first()
            )
            if not existing_membership:
                db.add(GroupMembership(**m))
                inserted += 1

        for a in assessments_payload:
            inserted += _upsert_snapshot(db, a)

        for r in relationships_payload:
            inserted += _upsert_relationship(db, r)

        existing_scenario = db.get(Scenario, scenario_payload["id"])
        if existing_scenario:
            for field, value in scenario_payload.items():
                setattr(existing_scenario, field, value)
        else:
            db.add(Scenario(**scenario_payload))
            inserted += 1

        existing_config = (
            db.query(SimulationConfig)
            .filter(SimulationConfig.prompt_version_key == config_payload["prompt_version_key"])
            .order_by(SimulationConfig.created_at.desc())
            .first()
        )
        if not existing_config:
            db.add(SimulationConfig(**config_payload))
            inserted += 1

        if inserted:
            db.commit()
        return {"inserted": inserted, "skipped": 0 if inserted else 1}

    # First-run full insert path.
    db.add_all(Person(**p) for p in people_payload)
    db.add(GroupContext(**group_payload))
    db.add_all(GroupMembership(**m) for m in memberships_payload)
    db.add_all(AssessmentSnapshot(**a) for a in assessments_payload)
    db.add_all(RelationshipEdge(**r) for r in relationships_payload)
    db.add(Scenario(**scenario_payload))
    config = SimulationConfig(**config_payload)
    db.add(config)
    db.flush()

    run = SimulationRun(
        id=run_payload["id"],
        group_id=run_payload["group_id"],
        scenario_id=run_payload["scenario_id"],
        simulation_config_id=config.id,
        generated_at_utc=_utcnow(),
        status=run_payload["status"],
        prompt_hash=run_payload["prompt_hash"],
        eval_evidence_anchoring_score=run_payload["eval_evidence_anchoring_score"],
        eval_internal_consistency_score=run_payload["eval_internal_consistency_score"],
        eval_plausibility_score=run_payload["eval_plausibility_score"],
        eval_intervention_usefulness_score=run_payload["eval_intervention_usefulness_score"],
        eval_uncertainty_quality_score=run_payload["eval_uncertainty_quality_score"],
        eval_rubric_notes=run_payload["eval_rubric_notes"],
    )
    db.add(run)
    db.flush()

    db.add(
        SimulationPass(
            run_id=run.id,
            pass_index=pass_payload["pass_index"],
            output_json=pass_payload["output_json"],
            missing_field_ids=pass_payload["missing_field_ids"],
            coverage_ratio=pass_payload["coverage_ratio"],
            overall_confidence=pass_payload["overall_confidence"],
        )
    )

    db.commit()
    return {"inserted": 1, "skipped": 0}
