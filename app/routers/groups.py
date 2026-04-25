from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import GroupContext, GroupMembership, Person

router = APIRouter(prefix="/groups", tags=["groups"])
templates = Jinja2Templates(directory="app/templates")


def _opt_int(v):
    if v is None or v == "" or v == "None":
        return None
    return int(v)


@router.get("/", response_class=HTMLResponse)
def list_groups(request: Request, db: Session = Depends(get_db)):
    groups = db.query(GroupContext).order_by(GroupContext.id).all()
    return templates.TemplateResponse(request, "groups/list.html", {"groups": groups})


@router.get("/new", response_class=HTMLResponse)
def new_group_form(request: Request, db: Session = Depends(get_db)):
    people = db.query(Person).order_by(Person.display_name).all()
    return templates.TemplateResponse(request, "groups/form.html", {"group": None, "people": people, "member_ids": [], "errors": []},
    )


@router.post("/new")
async def create_group(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    people = db.query(Person).order_by(Person.display_name).all()
    errors = []

    gid = form.get("id", "").strip()
    if not gid:
        errors.append("Group ID is required")
    elif db.get(GroupContext, gid):
        errors.append(f"Group ID '{gid}' already exists")

    stress = _opt_int(form.get("stress_level"))
    if stress is None or not (1 <= stress <= 5):
        errors.append("stress_level must be 1–5")

    if errors:
        return templates.TemplateResponse(request, "groups/form.html", {"group": None, "people": people, "member_ids": [], "errors": errors},
            status_code=422,
        )

    group = GroupContext(
        id=gid,
        type=form.get("type", "team"),
        structure=form.get("structure", "formal"),
        shared_goals=form.get("shared_goals", ""),
        norms_explicit=form.get("norms_explicit") or None,
        norms_implicit=form.get("norms_implicit") or None,
        decision_rules=form.get("decision_rules") or None,
        conflict_history=form.get("conflict_history") or None,
        stress_level=stress,
        role_clarity=_opt_int(form.get("role_clarity")),
        cultural_context=form.get("cultural_context") or None,
        environmental_constraints=form.get("environmental_constraints") or None,
    )
    db.add(group)
    db.flush()

    member_ids = form.getlist("member_ids")
    for pid in member_ids:
        if db.get(Person, pid):
            db.add(GroupMembership(group_id=gid, person_id=pid))

    db.commit()
    return RedirectResponse(url=f"/groups/{gid}", status_code=303)


@router.get("/{group_id}", response_class=HTMLResponse)
def view_group(group_id: str, request: Request, db: Session = Depends(get_db)):
    group = db.get(GroupContext, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    member_ids = [m.person_id for m in group.members]
    return templates.TemplateResponse(request, "groups/detail.html", {"group": group, "member_ids": member_ids},
    )


@router.get("/{group_id}/edit", response_class=HTMLResponse)
def edit_group_form(group_id: str, request: Request, db: Session = Depends(get_db)):
    group = db.get(GroupContext, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    people = db.query(Person).order_by(Person.display_name).all()
    member_ids = [m.person_id for m in group.members]
    return templates.TemplateResponse(request, "groups/form.html", {"group": group, "people": people, "member_ids": member_ids, "errors": []},
    )


@router.post("/{group_id}/edit")
async def update_group(group_id: str, request: Request, db: Session = Depends(get_db)):
    group = db.get(GroupContext, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    form = await request.form()
    people = db.query(Person).order_by(Person.display_name).all()

    stress = _opt_int(form.get("stress_level"))
    errors = []
    if stress is None or not (1 <= stress <= 5):
        errors.append("stress_level must be 1–5")
    if errors:
        member_ids = form.getlist("member_ids")
        return templates.TemplateResponse(request, "groups/form.html", {"group": group, "people": people, "member_ids": member_ids, "errors": errors},
            status_code=422,
        )

    group.type = form.get("type", group.type)
    group.structure = form.get("structure", group.structure)
    group.shared_goals = form.get("shared_goals", group.shared_goals)
    group.norms_explicit = form.get("norms_explicit") or None
    group.norms_implicit = form.get("norms_implicit") or None
    group.decision_rules = form.get("decision_rules") or None
    group.conflict_history = form.get("conflict_history") or None
    group.stress_level = stress
    group.role_clarity = _opt_int(form.get("role_clarity"))
    group.cultural_context = form.get("cultural_context") or None
    group.environmental_constraints = form.get("environmental_constraints") or None

    # Re-sync memberships
    for m in list(group.members):
        db.delete(m)
    db.flush()
    member_ids = form.getlist("member_ids")
    for pid in member_ids:
        if db.get(Person, pid):
            db.add(GroupMembership(group_id=group_id, person_id=pid))

    db.commit()
    return RedirectResponse(url=f"/groups/{group_id}", status_code=303)


@router.post("/{group_id}/delete")
def delete_group(group_id: str, db: Session = Depends(get_db)):
    group = db.get(GroupContext, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return RedirectResponse(url="/groups/", status_code=303)
