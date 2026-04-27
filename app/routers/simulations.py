from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from urllib.parse import quote_plus
from app.database import get_db
from app.models.entities import (
    SimulationRun, SimulationPass, GroupContext, Scenario, SimulationConfig
)
from app.services.prompt_builder import build_prompt, hash_prompt, generate_run_id
from app.services.validation import validate_run_inputs

router = APIRouter(prefix="/simulations", tags=["simulations"])
templates = Jinja2Templates(directory="app/templates")


def _opt_int(v) -> Optional[int]:
    if v is None or v == "" or v == "None":
        return None
    return int(v)


@router.get("/", response_class=HTMLResponse)
def list_runs(
    request: Request,
    group_id: Optional[str] = Query(default=None),
    scenario_id: Optional[str] = Query(default=None),
    prompt_version_key: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(SimulationRun)
    if group_id:
        query = query.filter(SimulationRun.group_id == group_id)
    if scenario_id:
        query = query.filter(SimulationRun.scenario_id == scenario_id)
    if prompt_version_key:
        query = query.join(SimulationConfig).filter(
            SimulationConfig.prompt_version_key == prompt_version_key
        )

    runs = query.order_by(SimulationRun.generated_at_utc.desc()).all()
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    scenarios = db.query(Scenario).order_by(Scenario.id).all()
    prompt_versions = [
        row[0]
        for row in db.query(SimulationConfig.prompt_version_key)
        .distinct()
        .order_by(SimulationConfig.prompt_version_key.desc())
        .all()
    ]
    return templates.TemplateResponse(
        request,
        "simulations/list.html",
        {
            "runs": runs,
            "groups": groups,
            "scenarios": scenarios,
            "prompt_versions": prompt_versions,
            "filters": {
                "group_id": group_id or "",
                "scenario_id": scenario_id or "",
                "prompt_version_key": prompt_version_key or "",
            },
        },
    )


@router.get("/new", response_class=HTMLResponse)
def new_run_form(request: Request, db: Session = Depends(get_db)):
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    scenarios = db.query(Scenario).order_by(Scenario.title).all()
    configs = db.query(SimulationConfig).order_by(SimulationConfig.created_at.desc()).all()
    return templates.TemplateResponse(request, "simulations/create.html", {"groups": groups, "scenarios": scenarios,
         "configs": configs, "errors": []},
    )


@router.post("/new")
async def create_run(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    scenarios = db.query(Scenario).order_by(Scenario.title).all()
    configs = db.query(SimulationConfig).order_by(SimulationConfig.created_at.desc()).all()

    group_id = form.get("group_id", "")
    scenario_id = form.get("scenario_id", "")
    config_id = form.get("simulation_config_id", "")

    errors = validate_run_inputs(db, group_id, scenario_id, config_id)
    if errors:
        return templates.TemplateResponse(request, "simulations/create.html", {"groups": groups, "scenarios": scenarios,
             "configs": configs, "errors": errors},
            status_code=422,
        )

    run_id = generate_run_id()
    run = SimulationRun(
        id=run_id,
        group_id=group_id,
        scenario_id=scenario_id,
        simulation_config_id=config_id,
        status="pending",
    )
    db.add(run)
    db.flush()

    # Build and hash the prompt
    try:
        prompt_text = build_prompt(db, run)
        run.prompt_hash = hash_prompt(prompt_text)
        run.status = "running"
    except Exception as e:
        run.status = "failed"
        db.commit()
        return templates.TemplateResponse(request, "simulations/create.html", {"groups": groups, "scenarios": scenarios,
             "configs": configs, "errors": [f"Prompt assembly failed: {e}"]},
            status_code=500,
        )

    db.commit()
    return RedirectResponse(url=f"/simulations/{run_id}", status_code=303)


@router.get("/{run_id}", response_class=HTMLResponse)
def view_run(run_id: str, request: Request, db: Session = Depends(get_db)):
    run = db.get(SimulationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    prompt_text = None
    if run.status in ("running", "complete", "failed_guardrail"):
        try:
            prompt_text = build_prompt(db, run)
        except Exception:
            pass

    latest_output = run.passes[-1].output_json if run.passes else None
    saved = request.query_params.get("saved")
    save_error = request.query_params.get("error")

    return templates.TemplateResponse(request, "simulations/detail.html", {
        "run": run,
        "prompt_text": prompt_text,
        "rubric_average": run.eval_rubric_average,
        "latest_output": latest_output,
        "saved": saved,
        "save_error": save_error,
    },
    )


@router.post("/{run_id}/evaluate")
async def save_evaluation(run_id: str, request: Request, db: Session = Depends(get_db)):
    run = db.get(SimulationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    form = await request.form()
    run.eval_evidence_anchoring_score = _opt_int(form.get("eval_evidence_anchoring_score"))
    run.eval_internal_consistency_score = _opt_int(form.get("eval_internal_consistency_score"))
    run.eval_plausibility_score = _opt_int(form.get("eval_plausibility_score"))
    run.eval_intervention_usefulness_score = _opt_int(form.get("eval_intervention_usefulness_score"))
    run.eval_uncertainty_quality_score = _opt_int(form.get("eval_uncertainty_quality_score"))
    run.eval_rubric_notes = form.get("eval_rubric_notes") or None

    # Determine run status from submitted output JSON if provided
    output_json_raw = form.get("output_json", "").strip()
    if output_json_raw:
        import json
        try:
            output_obj = json.loads(output_json_raw)
            run_status = output_obj.get("run_status", "ok")
            if run_status == "failed_guardrail":
                run.status = "failed_guardrail"
            else:
                run.status = "complete"

            config = run.simulation_config
            # Store each pass
            pass_obj = SimulationPass(
                run_id=run_id,
                pass_index=len(run.passes),
                output_json=output_obj,
                missing_field_ids=output_obj.get("evidence_coverage", {}).get("missing_field_ids"),
                coverage_ratio=output_obj.get("evidence_coverage", {}).get("coverage_ratio"),
                overall_confidence=output_obj.get("evidence_coverage", {}).get("overall_confidence"),
            )
            db.add(pass_obj)
        except json.JSONDecodeError:
            db.commit()
            return RedirectResponse(
                url=f"/simulations/{run_id}?saved=0&error={quote_plus('Output JSON is invalid. Please paste valid JSON.')}",
                status_code=303,
            )

    db.commit()
    return RedirectResponse(url=f"/simulations/{run_id}?saved=1", status_code=303)


@router.post("/{run_id}/delete")
def delete_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(SimulationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    db.delete(run)
    db.commit()
    return RedirectResponse(url="/simulations/", status_code=303)
