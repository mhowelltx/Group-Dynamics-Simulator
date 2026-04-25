import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import Scenario, GroupContext

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
templates = Jinja2Templates(directory="app/templates")


def _opt_int(v):
    if v is None or v == "" or v == "None":
        return None
    return int(v)


def _parse_list(raw: str) -> list:
    if not raw or not raw.strip():
        return []
    return [line.strip() for line in raw.strip().splitlines() if line.strip()]


@router.get("/", response_class=HTMLResponse)
def list_scenarios(request: Request, db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.title).all()
    return templates.TemplateResponse(request, "scenarios/list.html", {"scenarios": scenarios})


@router.get("/new", response_class=HTMLResponse)
def new_scenario_form(request: Request, db: Session = Depends(get_db)):
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    return templates.TemplateResponse(request, "scenarios/form.html", {"scenario": None, "groups": groups, "errors": []},
    )


@router.post("/new")
async def create_scenario(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    errors = []

    sid = form.get("id", "").strip()
    if not sid:
        errors.append("Scenario ID is required")
    elif db.get(Scenario, sid):
        errors.append(f"Scenario ID '{sid}' already exists")

    if errors:
        return templates.TemplateResponse(request, "scenarios/form.html", {"scenario": None, "groups": groups, "errors": errors},
            status_code=422,
        )

    group_id = form.get("group_id") or None

    scenario = Scenario(
        id=sid,
        title=form.get("title", ""),
        type=form.get("type", "other"),
        trigger_event=form.get("trigger_event", ""),
        stakes_level=_opt_int(form.get("stakes_level")) or 3,
        emotional_intensity=_opt_int(form.get("emotional_intensity")) or 3,
        ambiguity_level=_opt_int(form.get("ambiguity_level")) or 3,
        time_pressure=_opt_int(form.get("time_pressure")) or 3,
        resource_constraints=form.get("resource_constraints") or None,
        public_visibility=form.get("public_visibility") == "true",
        required_decision=form.get("required_decision", ""),
        success_criteria=form.get("success_criteria", ""),
        failure_consequences=form.get("failure_consequences", ""),
        known_facts=_parse_list(form.get("known_facts", "")),
        uncertain_facts=_parse_list(form.get("uncertain_facts", "")),
        intervention_options=_parse_list(form.get("intervention_options", "")),
        group_id=group_id,
    )
    db.add(scenario)
    db.commit()
    return RedirectResponse(url=f"/scenarios/{sid}", status_code=303)


@router.get("/{scenario_id}", response_class=HTMLResponse)
def view_scenario(scenario_id: str, request: Request, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return templates.TemplateResponse(request, "scenarios/detail.html", {"scenario": scenario})


@router.get("/{scenario_id}/edit", response_class=HTMLResponse)
def edit_scenario_form(scenario_id: str, request: Request, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    return templates.TemplateResponse(request, "scenarios/form.html", {"scenario": scenario, "groups": groups, "errors": []},
    )


@router.post("/{scenario_id}/edit")
async def update_scenario(scenario_id: str, request: Request, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    form = await request.form()
    scenario.title = form.get("title", scenario.title)
    scenario.type = form.get("type", scenario.type)
    scenario.trigger_event = form.get("trigger_event", scenario.trigger_event)
    scenario.stakes_level = _opt_int(form.get("stakes_level")) or scenario.stakes_level
    scenario.emotional_intensity = _opt_int(form.get("emotional_intensity")) or scenario.emotional_intensity
    scenario.ambiguity_level = _opt_int(form.get("ambiguity_level")) or scenario.ambiguity_level
    scenario.time_pressure = _opt_int(form.get("time_pressure")) or scenario.time_pressure
    scenario.resource_constraints = form.get("resource_constraints") or None
    scenario.public_visibility = form.get("public_visibility") == "true"
    scenario.required_decision = form.get("required_decision", scenario.required_decision)
    scenario.success_criteria = form.get("success_criteria", scenario.success_criteria)
    scenario.failure_consequences = form.get("failure_consequences", scenario.failure_consequences)
    scenario.known_facts = _parse_list(form.get("known_facts", ""))
    scenario.uncertain_facts = _parse_list(form.get("uncertain_facts", ""))
    scenario.intervention_options = _parse_list(form.get("intervention_options", ""))
    scenario.group_id = form.get("group_id") or None
    db.commit()
    return RedirectResponse(url=f"/scenarios/{scenario_id}", status_code=303)


@router.post("/{scenario_id}/delete")
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(scenario)
    db.commit()
    return RedirectResponse(url="/scenarios/", status_code=303)
