import re
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator

# ── Shared validators ─────────────────────────────────────────────────────────

SLUG_RE = re.compile(r"^[a-z0-9._-]{3,64}$")
PROMPT_VERSION_RE = re.compile(r"^P[0-9]+\.[0-9]+$")


def _check_slug(v: str) -> str:
    if not SLUG_RE.match(v):
        raise ValueError("ID must match pattern ^[a-z0-9._-]{3,64}$")
    return v


def _check_0_100(v: Optional[int], field: str) -> Optional[int]:
    if v is not None and not (0 <= v <= 100):
        raise ValueError(f"{field} must be 0..100")
    return v


def _check_1_5(v: Optional[int], field: str) -> Optional[int]:
    if v is not None and not (1 <= v <= 5):
        raise ValueError(f"{field} must be 1..5")
    return v


# ── Person ────────────────────────────────────────────────────────────────────

class PersonBase(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=120)
    role: str = Field(...)
    group_membership: str = Field(..., min_length=1, max_length=120)
    authority_level: int = Field(..., ge=1, le=5)
    is_active: bool = True

    @field_validator("role")
    @classmethod
    def role_enum(cls, v):
        allowed = ("leader", "manager", "ic", "advisor", "observer", "other")
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v


class PersonCreate(PersonBase):
    id: str

    @field_validator("id")
    @classmethod
    def id_slug(cls, v):
        return _check_slug(v)


class PersonUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=120)
    role: Optional[str] = None
    group_membership: Optional[str] = Field(None, min_length=1, max_length=120)
    authority_level: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None

    @field_validator("role")
    @classmethod
    def role_enum(cls, v):
        if v is None:
            return v
        allowed = ("leader", "manager", "ic", "advisor", "observer", "other")
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v


class PersonRead(PersonBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── AssessmentSnapshot ────────────────────────────────────────────────────────

class AssessmentSnapshotBase(BaseModel):
    person_id: str
    snapshot_date: Optional[datetime] = None
    evidence_source: str = "self_report"

    # Big Five
    big_five_openness: Optional[int] = Field(None, ge=0, le=100)
    big_five_conscientiousness: Optional[int] = Field(None, ge=0, le=100)
    big_five_extraversion: Optional[int] = Field(None, ge=0, le=100)
    big_five_agreeableness: Optional[int] = Field(None, ge=0, le=100)
    big_five_neuroticism: Optional[int] = Field(None, ge=0, le=100)

    # Conflict style
    conflict_competing: Optional[int] = Field(None, ge=0, le=100)
    conflict_collaborating: Optional[int] = Field(None, ge=0, le=100)
    conflict_compromising: Optional[int] = Field(None, ge=0, le=100)
    conflict_avoiding: Optional[int] = Field(None, ge=0, le=100)
    conflict_accommodating: Optional[int] = Field(None, ge=0, le=100)

    # Psych safety items (1..5 each)
    psych_safety_item_1: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_2: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_3: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_4: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_5: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_6: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_7: Optional[int] = Field(None, ge=1, le=5)

    # Communication style
    comm_directness: Optional[int] = Field(None, ge=0, le=100)
    comm_context_orientation: Optional[int] = Field(None, ge=0, le=100)
    comm_verbal_dominance: Optional[int] = Field(None, ge=0, le=100)
    comm_listening_quality: Optional[int] = Field(None, ge=0, le=100)
    comm_feedback_tolerance: Optional[int] = Field(None, ge=0, le=100)

    # Decision style
    decision_analytical_vs_intuitive: Optional[int] = Field(None, ge=0, le=100)
    decision_risk_appetite: Optional[int] = Field(None, ge=0, le=100)
    decision_speed: Optional[int] = Field(None, ge=0, le=100)
    decision_ambiguity_tolerance: Optional[int] = Field(None, ge=0, le=100)

    # EQ
    eq_perceiving: Optional[int] = Field(None, ge=0, le=100)
    eq_using: Optional[int] = Field(None, ge=0, le=100)
    eq_understanding: Optional[int] = Field(None, ge=0, le=100)
    eq_managing: Optional[int] = Field(None, ge=0, le=100)

    # Attachment
    attachment_secure: Optional[int] = Field(None, ge=0, le=100)
    attachment_anxious: Optional[int] = Field(None, ge=0, le=100)
    attachment_avoidant: Optional[int] = Field(None, ge=0, le=100)
    attachment_fearful: Optional[int] = Field(None, ge=0, le=100)

    notes: Optional[str] = None

    @field_validator("evidence_source")
    @classmethod
    def evidence_enum(cls, v):
        allowed = ("validated", "self_report", "observed", "inferred", "missing")
        if v not in allowed:
            raise ValueError(f"evidence_source must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def validate_conflict_sum(self):
        fields = [
            self.conflict_competing, self.conflict_collaborating,
            self.conflict_compromising, self.conflict_avoiding,
            self.conflict_accommodating,
        ]
        if all(f is not None for f in fields):
            total = sum(fields)
            if abs(total - 100) > 1:
                raise ValueError(
                    f"Conflict style values must sum to 100 ± 1 (got {total})"
                )
        return self

    @model_validator(mode="after")
    def validate_attachment_sum(self):
        fields = [
            self.attachment_secure, self.attachment_anxious,
            self.attachment_avoidant, self.attachment_fearful,
        ]
        if all(f is not None for f in fields):
            total = sum(fields)
            if abs(total - 100) > 1:
                raise ValueError(
                    f"Attachment values must sum to 100 ± 1 (got {total})"
                )
        return self

    @property
    def psych_safety_score(self) -> Optional[int]:
        items = [
            self.psych_safety_item_1, self.psych_safety_item_2,
            self.psych_safety_item_3, self.psych_safety_item_4,
            self.psych_safety_item_5, self.psych_safety_item_6,
            self.psych_safety_item_7,
        ]
        filled = [i for i in items if i is not None]
        if not filled:
            return None
        return round(100 * (sum(filled) / len(filled) - 1) / 4)


class AssessmentSnapshotCreate(AssessmentSnapshotBase):
    pass


class AssessmentSnapshotUpdate(BaseModel):
    evidence_source: Optional[str] = None
    big_five_openness: Optional[int] = Field(None, ge=0, le=100)
    big_five_conscientiousness: Optional[int] = Field(None, ge=0, le=100)
    big_five_extraversion: Optional[int] = Field(None, ge=0, le=100)
    big_five_agreeableness: Optional[int] = Field(None, ge=0, le=100)
    big_five_neuroticism: Optional[int] = Field(None, ge=0, le=100)
    conflict_competing: Optional[int] = Field(None, ge=0, le=100)
    conflict_collaborating: Optional[int] = Field(None, ge=0, le=100)
    conflict_compromising: Optional[int] = Field(None, ge=0, le=100)
    conflict_avoiding: Optional[int] = Field(None, ge=0, le=100)
    conflict_accommodating: Optional[int] = Field(None, ge=0, le=100)
    psych_safety_item_1: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_2: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_3: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_4: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_5: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_6: Optional[int] = Field(None, ge=1, le=5)
    psych_safety_item_7: Optional[int] = Field(None, ge=1, le=5)
    comm_directness: Optional[int] = Field(None, ge=0, le=100)
    comm_context_orientation: Optional[int] = Field(None, ge=0, le=100)
    comm_verbal_dominance: Optional[int] = Field(None, ge=0, le=100)
    comm_listening_quality: Optional[int] = Field(None, ge=0, le=100)
    comm_feedback_tolerance: Optional[int] = Field(None, ge=0, le=100)
    decision_analytical_vs_intuitive: Optional[int] = Field(None, ge=0, le=100)
    decision_risk_appetite: Optional[int] = Field(None, ge=0, le=100)
    decision_speed: Optional[int] = Field(None, ge=0, le=100)
    decision_ambiguity_tolerance: Optional[int] = Field(None, ge=0, le=100)
    eq_perceiving: Optional[int] = Field(None, ge=0, le=100)
    eq_using: Optional[int] = Field(None, ge=0, le=100)
    eq_understanding: Optional[int] = Field(None, ge=0, le=100)
    eq_managing: Optional[int] = Field(None, ge=0, le=100)
    attachment_secure: Optional[int] = Field(None, ge=0, le=100)
    attachment_anxious: Optional[int] = Field(None, ge=0, le=100)
    attachment_avoidant: Optional[int] = Field(None, ge=0, le=100)
    attachment_fearful: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class AssessmentSnapshotRead(AssessmentSnapshotBase):
    id: str
    missing_data_flag: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── RelationshipEdge ──────────────────────────────────────────────────────────

class RelationshipEdgeBase(BaseModel):
    from_person_id: str
    to_person_id: str
    trust: Optional[int] = Field(None, ge=0, le=100)
    influence: Optional[int] = Field(None, ge=0, le=100)
    emotional_closeness: Optional[int] = Field(None, ge=0, le=100)
    respect: Optional[int] = Field(None, ge=0, le=100)
    conflict_intensity: Optional[int] = Field(None, ge=0, le=100)
    dependency: Optional[int] = Field(None, ge=0, le=100)
    communication_frequency: Optional[int] = Field(None, ge=0, le=100)
    avoidance: Optional[int] = Field(None, ge=0, le=100)
    alliance: Optional[int] = Field(None, ge=0, le=100)
    power_differential: Optional[int] = Field(None, ge=0, le=100)
    evidence_source: str = "self_report"
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("evidence_source")
    @classmethod
    def evidence_enum(cls, v):
        allowed = ("validated", "self_report", "observed", "inferred", "missing")
        if v not in allowed:
            raise ValueError(f"evidence_source must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def no_self_edge(self):
        if self.from_person_id and self.to_person_id and self.from_person_id == self.to_person_id:
            raise ValueError("from_person_id and to_person_id must differ (no self-edges)")
        return self

    @property
    def health_score(self) -> Optional[int]:
        t = self.trust
        r = self.respect
        cf = self.communication_frequency
        ec = self.emotional_closeness
        ci = self.conflict_intensity
        av = self.avoidance
        pd = self.power_differential
        if all(v is not None for v in [t, r, cf, ec, ci, av, pd]):
            score = (
                0.25 * t
                + 0.20 * r
                + 0.15 * cf
                + 0.15 * ec
                + 0.10 * (100 - ci)
                + 0.10 * (100 - av)
                + 0.05 * (100 - pd)
            )
            return round(score)
        return None


class RelationshipEdgeCreate(RelationshipEdgeBase):
    pass


class RelationshipEdgeUpdate(BaseModel):
    trust: Optional[int] = Field(None, ge=0, le=100)
    influence: Optional[int] = Field(None, ge=0, le=100)
    emotional_closeness: Optional[int] = Field(None, ge=0, le=100)
    respect: Optional[int] = Field(None, ge=0, le=100)
    conflict_intensity: Optional[int] = Field(None, ge=0, le=100)
    dependency: Optional[int] = Field(None, ge=0, le=100)
    communication_frequency: Optional[int] = Field(None, ge=0, le=100)
    avoidance: Optional[int] = Field(None, ge=0, le=100)
    alliance: Optional[int] = Field(None, ge=0, le=100)
    power_differential: Optional[int] = Field(None, ge=0, le=100)
    evidence_source: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)


class RelationshipEdgeRead(RelationshipEdgeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── GroupContext ──────────────────────────────────────────────────────────────

class GroupContextBase(BaseModel):
    type: str
    structure: str
    shared_goals: str = Field(..., min_length=1, max_length=1000)
    norms_explicit: Optional[str] = None
    norms_implicit: Optional[str] = None
    decision_rules: Optional[str] = None
    conflict_history: Optional[str] = None
    stress_level: int = Field(..., ge=1, le=5)
    role_clarity: Optional[int] = Field(None, ge=0, le=100)
    cultural_context: Optional[str] = None
    environmental_constraints: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_enum(cls, v):
        allowed = ("team", "leadership_team", "project_team", "board", "other")
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

    @field_validator("structure")
    @classmethod
    def structure_enum(cls, v):
        allowed = ("formal", "informal", "hybrid")
        if v not in allowed:
            raise ValueError(f"structure must be one of {allowed}")
        return v


class GroupContextCreate(GroupContextBase):
    id: str
    member_ids: List[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def id_slug(cls, v):
        return _check_slug(v)


class GroupContextUpdate(BaseModel):
    type: Optional[str] = None
    structure: Optional[str] = None
    shared_goals: Optional[str] = Field(None, min_length=1, max_length=1000)
    norms_explicit: Optional[str] = None
    norms_implicit: Optional[str] = None
    decision_rules: Optional[str] = None
    conflict_history: Optional[str] = None
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    role_clarity: Optional[int] = Field(None, ge=0, le=100)
    cultural_context: Optional[str] = None
    environmental_constraints: Optional[str] = None
    member_ids: Optional[List[str]] = None


class GroupContextRead(GroupContextBase):
    id: str
    created_at: datetime
    updated_at: datetime
    member_ids: List[str] = Field(default_factory=list)
    model_config = {"from_attributes": True}


# ── Scenario ──────────────────────────────────────────────────────────────────

class ScenarioBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: str
    trigger_event: str = Field(..., min_length=1, max_length=2000)
    stakes_level: int = Field(..., ge=1, le=5)
    emotional_intensity: int = Field(..., ge=1, le=5)
    ambiguity_level: int = Field(..., ge=1, le=5)
    time_pressure: int = Field(..., ge=1, le=5)
    resource_constraints: Optional[str] = None
    public_visibility: bool = False
    required_decision: str = Field(..., min_length=1)
    success_criteria: str = Field(..., min_length=1)
    failure_consequences: str = Field(..., min_length=1)
    known_facts: Optional[List[str]] = None
    uncertain_facts: Optional[List[str]] = None
    intervention_options: Optional[List[str]] = None
    group_id: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_enum(cls, v):
        allowed = ("conflict", "decision", "change", "crisis", "performance", "other")
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v


class ScenarioCreate(ScenarioBase):
    id: str

    @field_validator("id")
    @classmethod
    def id_slug(cls, v):
        return _check_slug(v)


class ScenarioUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[str] = None
    trigger_event: Optional[str] = Field(None, min_length=1, max_length=2000)
    stakes_level: Optional[int] = Field(None, ge=1, le=5)
    emotional_intensity: Optional[int] = Field(None, ge=1, le=5)
    ambiguity_level: Optional[int] = Field(None, ge=1, le=5)
    time_pressure: Optional[int] = Field(None, ge=1, le=5)
    resource_constraints: Optional[str] = None
    public_visibility: Optional[bool] = None
    required_decision: Optional[str] = None
    success_criteria: Optional[str] = None
    failure_consequences: Optional[str] = None
    known_facts: Optional[List[str]] = None
    uncertain_facts: Optional[List[str]] = None
    intervention_options: Optional[List[str]] = None
    group_id: Optional[str] = None


class ScenarioRead(ScenarioBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── SimulationConfig ──────────────────────────────────────────────────────────

class SimulationConfigBase(BaseModel):
    prompt_version_key: str
    passes: int = Field(1, ge=1, le=10)
    randomness: str = "medium"
    depth: str = "standard"
    dialogue_enabled: bool = False
    report_detail_level: str = "standard"
    intervention_mode: str = "baseline"
    evidence_strictness: str = "moderate"
    guardrail_verbosity: str = "standard"

    @field_validator("prompt_version_key")
    @classmethod
    def version_key_format(cls, v):
        if not PROMPT_VERSION_RE.match(v):
            raise ValueError("prompt_version_key must match ^P[0-9]+\\.[0-9]+$")
        return v

    @field_validator("randomness")
    @classmethod
    def randomness_enum(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("randomness must be low, medium, or high")
        return v

    @field_validator("depth")
    @classmethod
    def depth_enum(cls, v):
        if v not in ("surface", "standard", "deep"):
            raise ValueError("depth must be surface, standard, or deep")
        return v

    @field_validator("report_detail_level")
    @classmethod
    def detail_enum(cls, v):
        if v not in ("summary", "standard", "full"):
            raise ValueError("report_detail_level must be summary, standard, or full")
        return v

    @field_validator("intervention_mode")
    @classmethod
    def intervention_enum(cls, v):
        if v not in ("baseline", "compare"):
            raise ValueError("intervention_mode must be baseline or compare")
        return v

    @field_validator("evidence_strictness")
    @classmethod
    def strictness_enum(cls, v):
        if v not in ("strict", "moderate", "lenient"):
            raise ValueError("evidence_strictness must be strict, moderate, or lenient")
        return v

    @field_validator("guardrail_verbosity")
    @classmethod
    def verbosity_enum(cls, v):
        if v not in ("minimal", "standard", "verbose"):
            raise ValueError("guardrail_verbosity must be minimal, standard, or verbose")
        return v


class SimulationConfigCreate(SimulationConfigBase):
    pass


class SimulationConfigRead(SimulationConfigBase):
    id: str
    created_at: datetime
    model_config = {"from_attributes": True}


# ── SimulationRun ─────────────────────────────────────────────────────────────

class SimulationRunCreate(BaseModel):
    group_id: str
    scenario_id: str
    simulation_config_id: str


class EvaluationUpdate(BaseModel):
    eval_evidence_anchoring_score: Optional[int] = Field(None, ge=1, le=5)
    eval_internal_consistency_score: Optional[int] = Field(None, ge=1, le=5)
    eval_plausibility_score: Optional[int] = Field(None, ge=1, le=5)
    eval_intervention_usefulness_score: Optional[int] = Field(None, ge=1, le=5)
    eval_uncertainty_quality_score: Optional[int] = Field(None, ge=1, le=5)
    eval_rubric_notes: Optional[str] = Field(None, max_length=1000)


class SimulationRunRead(BaseModel):
    id: str
    group_id: str
    scenario_id: str
    simulation_config_id: str
    generated_at_utc: datetime
    status: str
    prompt_hash: Optional[str]
    eval_evidence_anchoring_score: Optional[int]
    eval_internal_consistency_score: Optional[int]
    eval_plausibility_score: Optional[int]
    eval_intervention_usefulness_score: Optional[int]
    eval_uncertainty_quality_score: Optional[int]
    eval_rubric_notes: Optional[str]
    eval_rubric_average: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── SimulationPass ────────────────────────────────────────────────────────────

class SimulationPassCreate(BaseModel):
    run_id: str
    pass_index: int
    output_json: Any
    missing_field_ids: Optional[List[str]] = None
    coverage_ratio: Optional[float] = Field(None, ge=0.0, le=1.0)
    overall_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class SimulationPassRead(SimulationPassCreate):
    id: str
    created_at: datetime
    model_config = {"from_attributes": True}
