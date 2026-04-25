import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text,
    UniqueConstraint, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


# ── Enums ────────────────────────────────────────────────────────────────────

PERSON_ROLES = ("leader", "manager", "ic", "advisor", "observer", "other")
EVIDENCE_SOURCES = ("validated", "self_report", "observed", "inferred", "missing")
GROUP_TYPES = ("team", "leadership_team", "project_team", "board", "other")
GROUP_STRUCTURES = ("formal", "informal", "hybrid")
SCENARIO_TYPES = ("conflict", "decision", "change", "crisis", "performance", "other")
RANDOMNESS_LEVELS = ("low", "medium", "high")
DEPTH_LEVELS = ("surface", "standard", "deep")
DETAIL_LEVELS = ("summary", "standard", "full")
INTERVENTION_MODES = ("baseline", "compare")
STRICTNESS_LEVELS = ("strict", "moderate", "lenient")
VERBOSITY_LEVELS = ("minimal", "standard", "verbose")
RUN_STATUSES = ("pending", "running", "complete", "failed_guardrail", "failed")
TARGET_LEVELS = ("individual", "dyad", "group", "leader")


# ── Person ────────────────────────────────────────────────────────────────────

class Person(Base):
    __tablename__ = "persons"

    id = Column(String(64), primary_key=True)
    display_name = Column(String(120), nullable=False)
    role = Column(SAEnum(*PERSON_ROLES, name="person_role"), nullable=False)
    group_membership = Column(String(120), nullable=False)
    authority_level = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    assessments = relationship("AssessmentSnapshot", back_populates="person", cascade="all, delete-orphan")
    outgoing_edges = relationship("RelationshipEdge", foreign_keys="RelationshipEdge.from_person_id",
                                  back_populates="from_person", cascade="all, delete-orphan")
    incoming_edges = relationship("RelationshipEdge", foreign_keys="RelationshipEdge.to_person_id",
                                  back_populates="to_person", cascade="all, delete-orphan")
    group_memberships = relationship("GroupMembership", back_populates="person", cascade="all, delete-orphan")


# ── AssessmentSnapshot ────────────────────────────────────────────────────────

class AssessmentSnapshot(Base):
    __tablename__ = "assessment_snapshots"

    id = Column(String(36), primary_key=True, default=_uuid)
    person_id = Column(String(64), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(DateTime, default=_now, nullable=False)
    evidence_source = Column(SAEnum(*EVIDENCE_SOURCES, name="evidence_source"), nullable=False, default="self_report")

    # Big Five
    big_five_openness = Column(Integer, nullable=True)
    big_five_conscientiousness = Column(Integer, nullable=True)
    big_five_extraversion = Column(Integer, nullable=True)
    big_five_agreeableness = Column(Integer, nullable=True)
    big_five_neuroticism = Column(Integer, nullable=True)

    # Conflict style
    conflict_competing = Column(Integer, nullable=True)
    conflict_collaborating = Column(Integer, nullable=True)
    conflict_compromising = Column(Integer, nullable=True)
    conflict_avoiding = Column(Integer, nullable=True)
    conflict_accommodating = Column(Integer, nullable=True)

    # Psychological safety items (1–7, scale 1..5)
    psych_safety_item_1 = Column(Integer, nullable=True)
    psych_safety_item_2 = Column(Integer, nullable=True)
    psych_safety_item_3 = Column(Integer, nullable=True)
    psych_safety_item_4 = Column(Integer, nullable=True)
    psych_safety_item_5 = Column(Integer, nullable=True)
    psych_safety_item_6 = Column(Integer, nullable=True)
    psych_safety_item_7 = Column(Integer, nullable=True)

    # Communication style
    comm_directness = Column(Integer, nullable=True)
    comm_context_orientation = Column(Integer, nullable=True)
    comm_verbal_dominance = Column(Integer, nullable=True)
    comm_listening_quality = Column(Integer, nullable=True)
    comm_feedback_tolerance = Column(Integer, nullable=True)

    # Decision style
    decision_analytical_vs_intuitive = Column(Integer, nullable=True)
    decision_risk_appetite = Column(Integer, nullable=True)
    decision_speed = Column(Integer, nullable=True)
    decision_ambiguity_tolerance = Column(Integer, nullable=True)

    # Emotional intelligence
    eq_perceiving = Column(Integer, nullable=True)
    eq_using = Column(Integer, nullable=True)
    eq_understanding = Column(Integer, nullable=True)
    eq_managing = Column(Integer, nullable=True)

    # Attachment tendencies
    attachment_secure = Column(Integer, nullable=True)
    attachment_anxious = Column(Integer, nullable=True)
    attachment_avoidant = Column(Integer, nullable=True)
    attachment_fearful = Column(Integer, nullable=True)

    missing_data_flag = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    person = relationship("Person", back_populates="assessments")


# ── RelationshipEdge ──────────────────────────────────────────────────────────

class RelationshipEdge(Base):
    __tablename__ = "relationship_edges"
    __table_args__ = (UniqueConstraint("from_person_id", "to_person_id"),)

    id = Column(String(36), primary_key=True, default=_uuid)
    from_person_id = Column(String(64), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    to_person_id = Column(String(64), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)

    trust = Column(Integer, nullable=True)
    influence = Column(Integer, nullable=True)
    emotional_closeness = Column(Integer, nullable=True)
    respect = Column(Integer, nullable=True)
    conflict_intensity = Column(Integer, nullable=True)
    dependency = Column(Integer, nullable=True)
    communication_frequency = Column(Integer, nullable=True)
    avoidance = Column(Integer, nullable=True)
    alliance = Column(Integer, nullable=True)
    power_differential = Column(Integer, nullable=True)

    evidence_source = Column(SAEnum(*EVIDENCE_SOURCES, name="rel_evidence_source"), nullable=False, default="self_report")
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    from_person = relationship("Person", foreign_keys=[from_person_id], back_populates="outgoing_edges")
    to_person = relationship("Person", foreign_keys=[to_person_id], back_populates="incoming_edges")


# ── GroupContext ──────────────────────────────────────────────────────────────

class GroupContext(Base):
    __tablename__ = "group_contexts"

    id = Column(String(64), primary_key=True)
    type = Column(SAEnum(*GROUP_TYPES, name="group_type"), nullable=False)
    structure = Column(SAEnum(*GROUP_STRUCTURES, name="group_structure"), nullable=False)
    shared_goals = Column(Text, nullable=False)
    norms_explicit = Column(Text, nullable=True)
    norms_implicit = Column(Text, nullable=True)
    decision_rules = Column(Text, nullable=True)
    conflict_history = Column(Text, nullable=True)
    stress_level = Column(Integer, nullable=False)
    role_clarity = Column(Integer, nullable=True)
    cultural_context = Column(Text, nullable=True)
    environmental_constraints = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    members = relationship("GroupMembership", back_populates="group", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="group")
    simulation_runs = relationship("SimulationRun", back_populates="group")


class GroupMembership(Base):
    __tablename__ = "group_memberships"
    __table_args__ = (UniqueConstraint("group_id", "person_id"),)

    id = Column(String(36), primary_key=True, default=_uuid)
    group_id = Column(String(64), ForeignKey("group_contexts.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(String(64), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)

    group = relationship("GroupContext", back_populates="members")
    person = relationship("Person", back_populates="group_memberships")


# ── Scenario ──────────────────────────────────────────────────────────────────

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(64), primary_key=True)
    title = Column(String(200), nullable=False)
    type = Column(SAEnum(*SCENARIO_TYPES, name="scenario_type"), nullable=False)
    trigger_event = Column(Text, nullable=False)
    stakes_level = Column(Integer, nullable=False)
    emotional_intensity = Column(Integer, nullable=False)
    ambiguity_level = Column(Integer, nullable=False)
    time_pressure = Column(Integer, nullable=False)
    resource_constraints = Column(Text, nullable=True)
    public_visibility = Column(Boolean, nullable=False, default=False)
    required_decision = Column(Text, nullable=False)
    success_criteria = Column(Text, nullable=False)
    failure_consequences = Column(Text, nullable=False)
    known_facts = Column(JSON, nullable=True)
    uncertain_facts = Column(JSON, nullable=True)
    intervention_options = Column(JSON, nullable=True)
    group_id = Column(String(64), ForeignKey("group_contexts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    group = relationship("GroupContext", back_populates="scenarios")
    simulation_runs = relationship("SimulationRun", back_populates="scenario")


# ── SimulationConfig ──────────────────────────────────────────────────────────

class SimulationConfig(Base):
    __tablename__ = "simulation_configs"

    id = Column(String(36), primary_key=True, default=_uuid)
    prompt_version_key = Column(String(20), nullable=False)
    passes = Column(Integer, nullable=False, default=1)
    randomness = Column(SAEnum(*RANDOMNESS_LEVELS, name="randomness_level"), nullable=False, default="medium")
    depth = Column(SAEnum(*DEPTH_LEVELS, name="depth_level"), nullable=False, default="standard")
    dialogue_enabled = Column(Boolean, nullable=False, default=False)
    report_detail_level = Column(SAEnum(*DETAIL_LEVELS, name="detail_level"), nullable=False, default="standard")
    intervention_mode = Column(SAEnum(*INTERVENTION_MODES, name="intervention_mode"), nullable=False, default="baseline")
    evidence_strictness = Column(SAEnum(*STRICTNESS_LEVELS, name="strictness_level"), nullable=False, default="moderate")
    guardrail_verbosity = Column(SAEnum(*VERBOSITY_LEVELS, name="verbosity_level"), nullable=False, default="standard")
    created_at = Column(DateTime, default=_now, nullable=False)

    simulation_runs = relationship("SimulationRun", back_populates="simulation_config")


# ── SimulationRun ─────────────────────────────────────────────────────────────

class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(64), primary_key=True)
    group_id = Column(String(64), ForeignKey("group_contexts.id", ondelete="RESTRICT"), nullable=False)
    scenario_id = Column(String(64), ForeignKey("scenarios.id", ondelete="RESTRICT"), nullable=False)
    simulation_config_id = Column(String(36), ForeignKey("simulation_configs.id", ondelete="RESTRICT"), nullable=False)
    generated_at_utc = Column(DateTime, default=_now, nullable=False)
    status = Column(SAEnum(*RUN_STATUSES, name="run_status"), nullable=False, default="pending")
    prompt_hash = Column(String(64), nullable=True)

    # Evaluation fields
    eval_evidence_anchoring_score = Column(Integer, nullable=True)
    eval_internal_consistency_score = Column(Integer, nullable=True)
    eval_plausibility_score = Column(Integer, nullable=True)
    eval_intervention_usefulness_score = Column(Integer, nullable=True)
    eval_uncertainty_quality_score = Column(Integer, nullable=True)
    eval_rubric_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)

    group = relationship("GroupContext", back_populates="simulation_runs")
    scenario = relationship("Scenario", back_populates="simulation_runs")
    simulation_config = relationship("SimulationConfig", back_populates="simulation_runs")
    passes = relationship("SimulationPass", back_populates="run", cascade="all, delete-orphan",
                          order_by="SimulationPass.pass_index")

    @property
    def eval_rubric_average(self):
        scores = [
            self.eval_evidence_anchoring_score,
            self.eval_internal_consistency_score,
            self.eval_plausibility_score,
            self.eval_intervention_usefulness_score,
            self.eval_uncertainty_quality_score,
        ]
        filled = [s for s in scores if s is not None]
        if not filled:
            return None
        return round(sum(filled) / len(filled), 2)


# ── SimulationPass ────────────────────────────────────────────────────────────

class SimulationPass(Base):
    __tablename__ = "simulation_passes"

    id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(64), ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    pass_index = Column(Integer, nullable=False)
    output_json = Column(JSON, nullable=False)
    missing_field_ids = Column(JSON, nullable=True)
    coverage_ratio = Column(Float, nullable=True)
    overall_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    run = relationship("SimulationRun", back_populates="passes")
