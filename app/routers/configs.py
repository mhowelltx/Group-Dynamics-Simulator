from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import SimulationConfig
from app.schemas.entities import SimulationConfigCreate

router = APIRouter(prefix="/configs", tags=["configs"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_configs(request: Request, db: Session = Depends(get_db)):
    configs = db.query(SimulationConfig).order_by(SimulationConfig.created_at.desc()).all()
    return templates.TemplateResponse(request, "configs/list.html", {"configs": configs})


@router.get("/new", response_class=HTMLResponse)
def new_config_form(request: Request):
    return templates.TemplateResponse(request, "configs/form.html", {"config": None, "errors": []})


@router.post("/new")
async def create_config(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    errors = []

    try:
        data = SimulationConfigCreate(
            prompt_version_key=form.get("prompt_version_key", ""),
            passes=int(form.get("passes", 1)),
            randomness=form.get("randomness", "medium"),
            depth=form.get("depth", "standard"),
            dialogue_enabled=form.get("dialogue_enabled") == "true",
            report_detail_level=form.get("report_detail_level", "standard"),
            intervention_mode=form.get("intervention_mode", "baseline"),
            evidence_strictness=form.get("evidence_strictness", "moderate"),
            guardrail_verbosity=form.get("guardrail_verbosity", "standard"),
        )
    except Exception as e:
        errors = [str(e)]
        return templates.TemplateResponse(request, "configs/form.html", {"config": None, "errors": errors},
            status_code=422,
        )

    config = SimulationConfig(**data.model_dump())
    db.add(config)
    db.commit()
    return RedirectResponse(url="/configs/", status_code=303)


@router.post("/{config_id}/delete")
def delete_config(config_id: str, db: Session = Depends(get_db)):
    config = db.get(SimulationConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    db.delete(config)
    db.commit()
    return RedirectResponse(url="/configs/", status_code=303)
