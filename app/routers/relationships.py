from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.entities import RelationshipEdge, Person
from app.services.validation import validate_person_exists

router = APIRouter(prefix="/relationships", tags=["relationships"])
templates = Jinja2Templates(directory="app/templates")


def _opt_int(v) -> Optional[int]:
    if v is None or v == "" or v == "None":
        return None
    return int(v)


@router.get("/", response_class=HTMLResponse)
def list_relationships(request: Request, db: Session = Depends(get_db)):
    edges = (
        db.query(RelationshipEdge)
        .order_by(RelationshipEdge.from_person_id, RelationshipEdge.to_person_id)
        .all()
    )
    return templates.TemplateResponse(request, "relationships/list.html", {"edges": edges}
    )


@router.get("/new", response_class=HTMLResponse)
def new_edge_form(request: Request, db: Session = Depends(get_db)):
    people = db.query(Person).order_by(Person.display_name).all()
    return templates.TemplateResponse(request, "relationships/form.html", {"edge": None, "people": people, "errors": []},
    )


@router.post("/new")
async def create_edge(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    people = db.query(Person).order_by(Person.display_name).all()
    errors = []

    from_id = form.get("from_person_id", "")
    to_id = form.get("to_person_id", "")

    if from_id == to_id:
        errors.append("from_person_id and to_person_id must differ (no self-edges)")
    if err := validate_person_exists(db, from_id):
        errors.append(err)
    if err := validate_person_exists(db, to_id):
        errors.append(err)

    existing = (
        db.query(RelationshipEdge)
        .filter_by(from_person_id=from_id, to_person_id=to_id)
        .first()
    )
    if existing:
        errors.append(f"Relationship {from_id} → {to_id} already exists")

    if errors:
        return templates.TemplateResponse(request, "relationships/form.html", {"edge": None, "people": people, "errors": errors},
            status_code=422,
        )

    edge = RelationshipEdge(
        from_person_id=from_id,
        to_person_id=to_id,
        trust=_opt_int(form.get("trust")),
        influence=_opt_int(form.get("influence")),
        emotional_closeness=_opt_int(form.get("emotional_closeness")),
        respect=_opt_int(form.get("respect")),
        conflict_intensity=_opt_int(form.get("conflict_intensity")),
        dependency=_opt_int(form.get("dependency")),
        communication_frequency=_opt_int(form.get("communication_frequency")),
        avoidance=_opt_int(form.get("avoidance")),
        alliance=_opt_int(form.get("alliance")),
        power_differential=_opt_int(form.get("power_differential")),
        evidence_source=form.get("evidence_source", "self_report"),
        notes=form.get("notes") or None,
    )
    db.add(edge)
    db.commit()
    return RedirectResponse(url="/relationships/", status_code=303)


@router.get("/{edge_id}/edit", response_class=HTMLResponse)
def edit_edge_form(edge_id: str, request: Request, db: Session = Depends(get_db)):
    edge = db.get(RelationshipEdge, edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Relationship not found")
    people = db.query(Person).order_by(Person.display_name).all()
    return templates.TemplateResponse(request, "relationships/form.html", {"edge": edge, "people": people, "errors": []},
    )


@router.post("/{edge_id}/edit")
async def update_edge(edge_id: str, request: Request, db: Session = Depends(get_db)):
    edge = db.get(RelationshipEdge, edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Relationship not found")

    form = await request.form()
    for field in [
        "trust", "influence", "emotional_closeness", "respect", "conflict_intensity",
        "dependency", "communication_frequency", "avoidance", "alliance", "power_differential",
    ]:
        setattr(edge, field, _opt_int(form.get(field)))
    edge.evidence_source = form.get("evidence_source", edge.evidence_source)
    edge.notes = form.get("notes") or None
    db.commit()
    return RedirectResponse(url="/relationships/", status_code=303)


@router.post("/{edge_id}/delete")
def delete_edge(edge_id: str, db: Session = Depends(get_db)):
    edge = db.get(RelationshipEdge, edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(edge)
    db.commit()
    return RedirectResponse(url="/relationships/", status_code=303)
