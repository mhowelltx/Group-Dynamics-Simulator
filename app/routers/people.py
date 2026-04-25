from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.entities import Person
from app.schemas.entities import PersonCreate, PersonUpdate

router = APIRouter(prefix="/people", tags=["people"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_people(request: Request, db: Session = Depends(get_db)):
    people = db.query(Person).order_by(Person.display_name).all()
    return templates.TemplateResponse(request, "people/list.html", {"people": people})


@router.get("/new", response_class=HTMLResponse)
def new_person_form(request: Request):
    return templates.TemplateResponse(request, "people/form.html", {"person": None, "errors": []})


@router.post("/new")
def create_person(
    request: Request,
    id: str = Form(...),
    display_name: str = Form(...),
    role: str = Form(...),
    group_membership: str = Form(...),
    authority_level: int = Form(...),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
):
    errors = []
    try:
        data = PersonCreate(
            id=id, display_name=display_name, role=role,
            group_membership=group_membership, authority_level=authority_level,
            is_active=is_active,
        )
    except Exception as e:
        errors = [str(e)]
        return templates.TemplateResponse(request, "people/form.html", {"person": None, "errors": errors},
            status_code=422,
        )
    if db.get(Person, data.id):
        errors = [f"Person ID '{data.id}' already exists."]
        return templates.TemplateResponse(request, "people/form.html", {"person": None, "errors": errors},
            status_code=422,
        )
    person = Person(**data.model_dump())
    db.add(person)
    db.commit()
    return RedirectResponse(url=f"/people/{person.id}", status_code=303)


@router.get("/{person_id}", response_class=HTMLResponse)
def view_person(person_id: str, request: Request, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    assessments = sorted(person.assessments, key=lambda a: a.snapshot_date, reverse=True)
    return templates.TemplateResponse(request, "people/detail.html", {"person": person, "assessments": assessments},
    )


@router.get("/{person_id}/edit", response_class=HTMLResponse)
def edit_person_form(person_id: str, request: Request, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return templates.TemplateResponse(request, "people/form.html", {"person": person, "errors": []})


@router.post("/{person_id}/edit")
def update_person(
    person_id: str,
    request: Request,
    display_name: str = Form(...),
    role: str = Form(...),
    group_membership: str = Form(...),
    authority_level: int = Form(...),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    errors = []
    try:
        data = PersonUpdate(
            display_name=display_name, role=role,
            group_membership=group_membership, authority_level=authority_level,
            is_active=is_active,
        )
    except Exception as e:
        errors = [str(e)]
        return templates.TemplateResponse(request, "people/form.html", {"person": person, "errors": errors},
            status_code=422,
        )
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(person, field, value)
    db.commit()
    return RedirectResponse(url=f"/people/{person_id}", status_code=303)


@router.post("/{person_id}/delete")
def delete_person(person_id: str, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
    return RedirectResponse(url="/people/", status_code=303)
