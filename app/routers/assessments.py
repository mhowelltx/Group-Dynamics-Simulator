from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.entities import AssessmentSnapshot, Person
from app.services.validation import compute_missing_data_flag, preflight_assessment

router = APIRouter(prefix="/assessments", tags=["assessments"])
templates = Jinja2Templates(directory="app/templates")


def _opt_int(v) -> Optional[int]:
    if v is None or v == "" or v == "None":
        return None
    return int(v)


@router.get("/new", response_class=HTMLResponse)
def new_assessment_form(request: Request, person_id: Optional[str] = None, db: Session = Depends(get_db)):
    people = db.query(Person).order_by(Person.display_name).all()
    return templates.TemplateResponse(request, "assessments/form.html", {"snapshot": None, "people": people,
         "selected_person_id": person_id, "errors": []},
    )


@router.post("/new")
async def create_assessment(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    people = db.query(Person).order_by(Person.display_name).all()

    person_id = form.get("person_id", "")
    if not db.get(Person, person_id):
        return templates.TemplateResponse(request, "assessments/form.html", {"snapshot": None, "people": people,
             "selected_person_id": person_id, "errors": [f"Person '{person_id}' not found"]},
            status_code=422,
        )

    data = {
        "person_id": person_id,
        "evidence_source": form.get("evidence_source", "self_report"),
        "big_five_openness": _opt_int(form.get("big_five_openness")),
        "big_five_conscientiousness": _opt_int(form.get("big_five_conscientiousness")),
        "big_five_extraversion": _opt_int(form.get("big_five_extraversion")),
        "big_five_agreeableness": _opt_int(form.get("big_five_agreeableness")),
        "big_five_neuroticism": _opt_int(form.get("big_five_neuroticism")),
        "conflict_competing": _opt_int(form.get("conflict_competing")),
        "conflict_collaborating": _opt_int(form.get("conflict_collaborating")),
        "conflict_compromising": _opt_int(form.get("conflict_compromising")),
        "conflict_avoiding": _opt_int(form.get("conflict_avoiding")),
        "conflict_accommodating": _opt_int(form.get("conflict_accommodating")),
        "psych_safety_item_1": _opt_int(form.get("psych_safety_item_1")),
        "psych_safety_item_2": _opt_int(form.get("psych_safety_item_2")),
        "psych_safety_item_3": _opt_int(form.get("psych_safety_item_3")),
        "psych_safety_item_4": _opt_int(form.get("psych_safety_item_4")),
        "psych_safety_item_5": _opt_int(form.get("psych_safety_item_5")),
        "psych_safety_item_6": _opt_int(form.get("psych_safety_item_6")),
        "psych_safety_item_7": _opt_int(form.get("psych_safety_item_7")),
        "comm_directness": _opt_int(form.get("comm_directness")),
        "comm_context_orientation": _opt_int(form.get("comm_context_orientation")),
        "comm_verbal_dominance": _opt_int(form.get("comm_verbal_dominance")),
        "comm_listening_quality": _opt_int(form.get("comm_listening_quality")),
        "comm_feedback_tolerance": _opt_int(form.get("comm_feedback_tolerance")),
        "decision_analytical_vs_intuitive": _opt_int(form.get("decision_analytical_vs_intuitive")),
        "decision_risk_appetite": _opt_int(form.get("decision_risk_appetite")),
        "decision_speed": _opt_int(form.get("decision_speed")),
        "decision_ambiguity_tolerance": _opt_int(form.get("decision_ambiguity_tolerance")),
        "eq_perceiving": _opt_int(form.get("eq_perceiving")),
        "eq_using": _opt_int(form.get("eq_using")),
        "eq_understanding": _opt_int(form.get("eq_understanding")),
        "eq_managing": _opt_int(form.get("eq_managing")),
        "attachment_secure": _opt_int(form.get("attachment_secure")),
        "attachment_anxious": _opt_int(form.get("attachment_anxious")),
        "attachment_avoidant": _opt_int(form.get("attachment_avoidant")),
        "attachment_fearful": _opt_int(form.get("attachment_fearful")),
        "notes": form.get("notes") or None,
    }

    errors = preflight_assessment(data)
    if errors:
        return templates.TemplateResponse(request, "assessments/form.html", {"snapshot": None, "people": people,
             "selected_person_id": person_id, "errors": errors},
            status_code=422,
        )

    data["missing_data_flag"] = compute_missing_data_flag(data)
    snap = AssessmentSnapshot(**data)
    db.add(snap)
    db.commit()
    return RedirectResponse(url=f"/people/{person_id}", status_code=303)


@router.get("/{snapshot_id}/edit", response_class=HTMLResponse)
def edit_assessment_form(snapshot_id: str, request: Request, db: Session = Depends(get_db)):
    snap = db.get(AssessmentSnapshot, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Assessment not found")
    people = db.query(Person).order_by(Person.display_name).all()
    return templates.TemplateResponse(request, "assessments/form.html", {"snapshot": snap, "people": people,
         "selected_person_id": snap.person_id, "errors": []},
    )


@router.post("/{snapshot_id}/edit")
async def update_assessment(snapshot_id: str, request: Request, db: Session = Depends(get_db)):
    snap = db.get(AssessmentSnapshot, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Assessment not found")

    form = await request.form()
    people = db.query(Person).order_by(Person.display_name).all()

    data = {
        "big_five_openness": _opt_int(form.get("big_five_openness")),
        "big_five_conscientiousness": _opt_int(form.get("big_five_conscientiousness")),
        "big_five_extraversion": _opt_int(form.get("big_five_extraversion")),
        "big_five_agreeableness": _opt_int(form.get("big_five_agreeableness")),
        "big_five_neuroticism": _opt_int(form.get("big_five_neuroticism")),
        "conflict_competing": _opt_int(form.get("conflict_competing")),
        "conflict_collaborating": _opt_int(form.get("conflict_collaborating")),
        "conflict_compromising": _opt_int(form.get("conflict_compromising")),
        "conflict_avoiding": _opt_int(form.get("conflict_avoiding")),
        "conflict_accommodating": _opt_int(form.get("conflict_accommodating")),
        "psych_safety_item_1": _opt_int(form.get("psych_safety_item_1")),
        "psych_safety_item_2": _opt_int(form.get("psych_safety_item_2")),
        "psych_safety_item_3": _opt_int(form.get("psych_safety_item_3")),
        "psych_safety_item_4": _opt_int(form.get("psych_safety_item_4")),
        "psych_safety_item_5": _opt_int(form.get("psych_safety_item_5")),
        "psych_safety_item_6": _opt_int(form.get("psych_safety_item_6")),
        "psych_safety_item_7": _opt_int(form.get("psych_safety_item_7")),
        "comm_directness": _opt_int(form.get("comm_directness")),
        "comm_context_orientation": _opt_int(form.get("comm_context_orientation")),
        "comm_verbal_dominance": _opt_int(form.get("comm_verbal_dominance")),
        "comm_listening_quality": _opt_int(form.get("comm_listening_quality")),
        "comm_feedback_tolerance": _opt_int(form.get("comm_feedback_tolerance")),
        "decision_analytical_vs_intuitive": _opt_int(form.get("decision_analytical_vs_intuitive")),
        "decision_risk_appetite": _opt_int(form.get("decision_risk_appetite")),
        "decision_speed": _opt_int(form.get("decision_speed")),
        "decision_ambiguity_tolerance": _opt_int(form.get("decision_ambiguity_tolerance")),
        "eq_perceiving": _opt_int(form.get("eq_perceiving")),
        "eq_using": _opt_int(form.get("eq_using")),
        "eq_understanding": _opt_int(form.get("eq_understanding")),
        "eq_managing": _opt_int(form.get("eq_managing")),
        "attachment_secure": _opt_int(form.get("attachment_secure")),
        "attachment_anxious": _opt_int(form.get("attachment_anxious")),
        "attachment_avoidant": _opt_int(form.get("attachment_avoidant")),
        "attachment_fearful": _opt_int(form.get("attachment_fearful")),
        "evidence_source": form.get("evidence_source", snap.evidence_source),
        "notes": form.get("notes") or None,
    }

    errors = preflight_assessment(data)
    if errors:
        return templates.TemplateResponse(request, "assessments/form.html", {"snapshot": snap, "people": people,
             "selected_person_id": snap.person_id, "errors": errors},
            status_code=422,
        )

    data["missing_data_flag"] = compute_missing_data_flag(data)
    for field, value in data.items():
        setattr(snap, field, value)
    db.commit()
    return RedirectResponse(url=f"/people/{snap.person_id}", status_code=303)


@router.post("/{snapshot_id}/delete")
def delete_assessment(snapshot_id: str, db: Session = Depends(get_db)):
    snap = db.get(AssessmentSnapshot, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Assessment not found")
    person_id = snap.person_id
    db.delete(snap)
    db.commit()
    return RedirectResponse(url=f"/people/{person_id}", status_code=303)
