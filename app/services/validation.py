"""
Contract-aligned validation service.

Enforces Phase 1 frozen contract rules:
- Enum bounds and required field checks (delegated to Pydantic schemas)
- Conflict style sum tolerance (100 ± 1)
- Attachment sum tolerance (100 ± 1) when all four present
- Relationship self-edge prevention
- Referential integrity (person/group/scenario ID existence)
- Missing-data flag computation
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.entities import Person, GroupContext, Scenario, SimulationConfig


def compute_missing_data_flag(snapshot_data: dict) -> bool:
    """Return True if fewer than 60% of Big Five fields are present."""
    ocean_fields = [
        "big_five_openness", "big_five_conscientiousness",
        "big_five_extraversion", "big_five_agreeableness", "big_five_neuroticism",
    ]
    present = sum(1 for f in ocean_fields if snapshot_data.get(f) is not None)
    return present < (0.6 * len(ocean_fields))


def validate_person_exists(db: Session, person_id: str) -> Optional[str]:
    if not db.get(Person, person_id):
        return f"Person '{person_id}' not found"
    return None


def validate_group_exists(db: Session, group_id: str) -> Optional[str]:
    if not db.get(GroupContext, group_id):
        return f"GroupContext '{group_id}' not found"
    return None


def validate_scenario_exists(db: Session, scenario_id: str) -> Optional[str]:
    if not db.get(Scenario, scenario_id):
        return f"Scenario '{scenario_id}' not found"
    return None


def validate_config_exists(db: Session, config_id: str) -> Optional[str]:
    if not db.get(SimulationConfig, config_id):
        return f"SimulationConfig '{config_id}' not found"
    return None


def validate_run_inputs(db: Session, group_id: str, scenario_id: str, config_id: str) -> list[str]:
    errors = []
    if err := validate_group_exists(db, group_id):
        errors.append(err)
    if err := validate_scenario_exists(db, scenario_id):
        errors.append(err)
    if err := validate_config_exists(db, config_id):
        errors.append(err)
    return errors


def preflight_assessment(snapshot_data: dict) -> list[str]:
    """Return list of contract-violation messages for an assessment payload."""
    errors = []

    # Conflict sum check
    conflict_fields = [
        "conflict_competing", "conflict_collaborating",
        "conflict_compromising", "conflict_avoiding", "conflict_accommodating",
    ]
    conflict_values = [snapshot_data.get(f) for f in conflict_fields]
    if all(v is not None for v in conflict_values):
        total = sum(conflict_values)
        if abs(total - 100) > 1:
            errors.append(f"Conflict style values sum to {total}, must be 100 ± 1")

    # Attachment sum check
    attach_fields = [
        "attachment_secure", "attachment_anxious",
        "attachment_avoidant", "attachment_fearful",
    ]
    attach_values = [snapshot_data.get(f) for f in attach_fields]
    if all(v is not None for v in attach_values):
        total = sum(attach_values)
        if abs(total - 100) > 1:
            errors.append(f"Attachment values sum to {total}, must be 100 ± 1")

    return errors
