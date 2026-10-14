import os
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from . import store, domain

class Mutation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int | None = Field(default=None, ge=0)
class Simulation(Mutation):
    scenario: Literal["brute_force", "phishing", "ransomware", "lateral"]
    run_id: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9_-]+$")
class IncidentUpdate(Mutation):
    status: Literal["new", "investigating", "resolved"] | None = None
    step: int | None = Field(default=None, ge=0, le=2)


def create_app(database_url=None, static_dir=None):
    app = FastAPI(title="CODEX DEMO API", version="1.0.0")
    engine = store.connect(database_url or os.getenv("DATABASE_URL", "sqlite:///./demo.db"))
    app.state.engine = engine
    @app.exception_handler(store.Conflict)
    async def conflict(_, exc):
        return JSONResponse(status_code=409, content={"detail":"Demo zmieniono w innej karcie. Odśwież stan i spróbuj ponownie."})
    @app.get("/api/health")
    def health():
        with engine.connect() as conn: conn.execute(text("SELECT 1"))
        return {"status":"ok", "mode":"demo", "schemaVersion":1, "externalServices":False}
    @app.get("/api/state")
    def state(): return store.read(engine)
    @app.post("/api/reset")
    def reset(body: Mutation): return store.reset(engine, body.expected_revision)
    @app.get("/api/export")
    def export():
        return JSONResponse(store.read(engine)["data"], headers={"Content-Disposition":"attachment; filename=demo-report.json"})
    @app.post("/api/simulate")
    def simulate(body: Simulation):
        return store.mutate(engine, lambda d: domain.simulate(d, body.scenario, body.run_id), body.expected_revision)
    @app.patch("/api/incidents/{incident_id}")
    def incident(incident_id: str, body: IncidentUpdate):
        if body.status is None and body.step is None: raise HTTPException(422, "Provide status or step")
        def change(data):
            row = next((i for i in data["incidents"] if i["id"] == incident_id), None)
            if row is None: raise HTTPException(404, "Incident not found")
            domain.update_incident(data, incident_id, body.status, body.step)
        return store.mutate(engine, change, body.expected_revision)
    static = Path(static_dir or os.getenv("DEMO_STATIC_DIR", str(store.ROOT / "static")))
    if static.is_dir(): app.mount("/", StaticFiles(directory=static, html=True), name="frontend")
    return app

app = create_app()
