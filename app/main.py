from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import init_db, SessionLocal
from app.seed import seed_test_data, should_seed_test_data
from app.models.entities import Person, GroupContext, Scenario, SimulationRun
from app.routers import people, assessments, relationships, groups, scenarios, configs, simulations

app = FastAPI(title="Group Dynamics Simulator", version="2.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Register routers
app.include_router(people.router)
app.include_router(assessments.router)
app.include_router(relationships.router)
app.include_router(groups.router)
app.include_router(scenarios.router)
app.include_router(configs.router)
app.include_router(simulations.router)


@app.on_event("startup")
def on_startup():
    init_db()
    if should_seed_test_data():
        db: Session = SessionLocal()
        try:
            seed_test_data(db)
        finally:
            db.close()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db: Session = SessionLocal()
    try:
        stats = {
            "people": db.query(Person).count(),
            "groups": db.query(GroupContext).count(),
            "scenarios": db.query(Scenario).count(),
            "runs": db.query(SimulationRun).count(),
        }
        recent_runs = (
            db.query(SimulationRun)
            .order_by(SimulationRun.generated_at_utc.desc())
            .limit(10)
            .all()
        )
    finally:
        db.close()
    return templates.TemplateResponse(request, "index.html", {"stats": stats, "recent_runs": recent_runs},
    )
