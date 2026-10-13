from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_session
from .models import Equipment, Incident, utc_now
from .schemas import (
    EquipmentCreate,
    EquipmentRead,
    IncidentCreate,
    IncidentRead,
    IncidentStatus,
    IncidentUpdate,
    Severity,
    SummaryRead,
)

app = FastAPI(title="LabPulse", version="1.0.0")
SessionDep = Annotated[Session, Depends(get_session)]
Instrumentator(excluded_handlers=["/health", "/ready", "/metrics"]).instrument(
    app
).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "LabPulse", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(session: SessionDep) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready"}


def get_equipment_or_404(session: Session, equipment_id: int) -> Equipment:
    equipment = session.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="equipment not found")
    return equipment


def get_incident_or_404(session: Session, incident_id: int) -> Incident:
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return incident


def sync_equipment_status(session: Session, equipment: Equipment) -> None:
    severities = session.scalars(
        select(Incident.severity).where(
            Incident.equipment_id == equipment.id,
            Incident.status != "resolved",
        )
    ).all()
    if any(level in ("high", "critical") for level in severities):
        equipment.status = "offline"
    elif severities:
        equipment.status = "attention"
    else:
        equipment.status = "operational"


@app.get("/api/equipment", response_model=list[EquipmentRead])
def list_equipment(session: SessionDep) -> list[Equipment]:
    return list(session.scalars(select(Equipment).order_by(Equipment.code)).all())


@app.post("/api/equipment", response_model=EquipmentRead, status_code=201)
def create_equipment(payload: EquipmentCreate, session: SessionDep) -> Equipment:
    equipment = Equipment(**{**payload.model_dump(), "code": payload.code.upper()})
    session.add(equipment)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="equipment code already exists"
        ) from exc
    session.refresh(equipment)
    return equipment


@app.get("/api/equipment/{equipment_id}", response_model=EquipmentRead)
def get_equipment(equipment_id: int, session: SessionDep) -> Equipment:
    return get_equipment_or_404(session, equipment_id)


@app.get("/api/incidents", response_model=list[IncidentRead])
def list_incidents(
    session: SessionDep,
    status: Annotated[IncidentStatus | None, Query()] = None,
    severity: Annotated[Severity | None, Query()] = None,
    equipment_id: Annotated[int | None, Query()] = None,
) -> list[Incident]:
    query = select(Incident)
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if equipment_id is not None:
        query = query.where(Incident.equipment_id == equipment_id)
    return list(
        session.scalars(
            query.order_by(Incident.created_at.desc(), Incident.id.desc())
        ).all()
    )


@app.post("/api/incidents", response_model=IncidentRead, status_code=201)
def create_incident(payload: IncidentCreate, session: SessionDep) -> Incident:
    equipment = get_equipment_or_404(session, payload.equipment_id)
    incident = Incident(**payload.model_dump(), status="open")
    session.add(incident)
    session.flush()
    sync_equipment_status(session, equipment)
    session.commit()
    session.refresh(incident)
    return incident


@app.get("/api/incidents/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, session: SessionDep) -> Incident:
    return get_incident_or_404(session, incident_id)


@app.put("/api/incidents/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int, payload: IncidentUpdate, session: SessionDep
) -> Incident:
    incident = get_incident_or_404(session, incident_id)
    incident.status = payload.status
    incident.resolved_at = utc_now() if payload.status == "resolved" else None
    session.flush()
    sync_equipment_status(session, incident.equipment)
    session.commit()
    session.refresh(incident)
    return incident


@app.delete("/api/incidents/{incident_id}", status_code=204)
def delete_incident(incident_id: int, session: SessionDep) -> Response:
    incident = get_incident_or_404(session, incident_id)
    equipment = incident.equipment
    session.delete(incident)
    session.flush()
    sync_equipment_status(session, equipment)
    session.commit()
    return Response(status_code=204)


@app.get("/api/summary", response_model=SummaryRead)
def summary(session: SessionDep) -> SummaryRead:
    counts = {
        status: count
        for status, count in session.execute(
            select(Equipment.status, func.count()).group_by(Equipment.status)
        ).all()
    }
    open_count = (
        session.scalar(
            select(func.count())
            .select_from(Incident)
            .where(Incident.status != "resolved")
        )
        or 0
    )
    resolved_count = (
        session.scalar(
            select(func.count())
            .select_from(Incident)
            .where(Incident.status == "resolved")
        )
        or 0
    )
    return SummaryRead(
        equipment_total=sum(counts.values()),
        operational=counts.get("operational", 0),
        attention=counts.get("attention", 0),
        offline=counts.get("offline", 0),
        open_incidents=open_count,
        resolved_incidents=resolved_count,
    )
